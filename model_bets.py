import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn import linear_model
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_val_score

import betting as u

#np.random.seed(6)
df_start = pd.read_csv('final.csv', sep=',')
df2020=pd.read_csv("final_2020.csv", sep=',')
df_start = pd.concat([df_start, df2020],ignore_index=True)


df_start=df_start[["rank","p1","p2","fs","w1sp","w2sp","wrp","wsp","tpw","aces","df","bpc","bps","bpo","bpw","tmw","complete","serveadv","fatigue","h2h","uncertainty","winner","p1_odd","p2_odd","year","tourney_id"]]
list_features=["fs","w1sp","w2sp","wrp","wsp","tpw","aces","df","bpc","bps","bpo","bpw","tmw","complete","serveadv","fatigue"]
#list_features=["rank"] 
#excluding rank seem to be bad for logloss but beneficial for roi!
#not used: rank, h2h

to_sel=list_features+["p1","p2","uncertainty","winner","p1_odd","p2_odd","year","tourney_id"]
df=df_start[to_sel]#.sample(frac=1)
#df["isGrandSlam"] = df["tourney_id"].apply(lambda x : 1 if x in {49.0,36.0,31.0,6.0} else 0)

#train
df_train=df[df['year']<2017]
#take only % of less uncertain matches
#df_train=df_train[df_train["tourney_id"].isin([6,31,36,49,19,20,23,25,29,46,47,56,64])] #Grand Slams + Master 1000 only!!!
df_train=df_train.sort_values(by=["uncertainty"])[0:round(df_train.shape[0]*0.25)].reset_index(drop=True)
#extract label
y_train = df_train["winner"]
#drop columns not representing actual features 
train=df_train.drop(["p1","p2","p1_odd","p2_odd","winner","uncertainty","year","tourney_id"], axis=1)

#validation 
df_val=df[(df['year'].isin([2017,2018,2019]))].reset_index(drop=True)
#SPECIAL VALIDATION SET: Rafa Nadal's matches
#df_val=df_val[((df_val["p1"] == "Rafael Nadal") | (df_val["p2"] == "Rafael Nadal"))].reset_index(drop=True)
top_players_list_2017_2018 = ["Rafael Nadal","Roger Federer","Novak Djokovic","Dominic Thiem","Daniil Medvedev","Alexander Zverev",\
 "Juan Martin del Potro","Kevin Anderson", "Marin Cilic","Grigor Dimitrov"]
#top_players_list_2019 = ["Rafael Nadal","Roger Federer","Novak Djokovic","Dominic Thiem","Daniil Medvedev","Alexander Zverev",\
# "Juan Martin del Potro","Kevin Anderson", "Stefanos Tsitsipas","Matteo Berrettini"]
#redefined: best players of the two years 19-20
#top_players_list_2019 = ["Rafael Nadal","Roger Federer","Novak Djokovic","Dominic Thiem","Daniil Medvedev", "Alexander Zverev", "Stefanos Tsitsipas"]#,"Matteo Berrettini"]
top_players_list_2020=["Rafael Nadal","Roger Federer","Novak Djokovic","Dominic Thiem","Daniil Medvedev","Alexander Zverev",\
 "Stefanos Tsitsipas","Andrey Rublev"]
df_val=df_val[((df_val["p1"].isin(top_players_list_2017_2018))\
 | (df_val["p2"].isin(top_players_list_2017_2018)))].reset_index(drop=True)

df_val=df_val[df_val["tourney_id"].isin([6,31,36,49,19,20,23,25,29,46,47,56,64])] #Grand Slams + Master 1000 only!!!
df_val=df_val.sort_values(by=["uncertainty"])[0:round(df_val.shape[0]*0.5)].reset_index(drop=True)
y_val = df_val["winner"]
metadata=df_val[["p1","p2","p1_odd","p2_odd","uncertainty","year"]]
val=df_val.drop(["p1","p2","p1_odd","p2_odd","winner","uncertainty","year","tourney_id"], axis=1)


print('\nTraining samples: {} Testing samples: {}'.format(train.shape[0],val.shape[0]))

#Logistic Regression model
print("\nLogistic regression")
clf = make_pipeline(StandardScaler(), linear_model.LogisticRegressionCV(cv=5, max_iter=400, random_state=6)).fit(train,y_train)
y_hat_train=clf.predict(train)
print("Training accuracy:",metrics.accuracy_score(y_train, y_hat_train))
y_hat_val=clf.predict(val)
print("Validation accuracy:",metrics.accuracy_score(y_val, y_hat_val))
#print(y_hat_val)
probs=clf.predict_proba(val)

loss=metrics.log_loss(y_val,probs)
print("Logistic loss: {}".format(loss))


#now we have the estimated probability of victory of each player in all test matches

#dataframe for ROI evaluation
columns=["p0","p1","prob0","prob1","odd0","odd1","label"]#,"uncertainty"]
bets=pd.DataFrame(columns=columns)
for i in range(probs.shape[0]):
	v=[]
	v.append(metadata.loc[i,"p1"])
	v.append(metadata.loc[i,"p2"])
	v.append(probs[i,0])
	v.append(probs[i,1])
	v.append(metadata.loc[i,"p1_odd"])
	v.append(metadata.loc[i,"p2_odd"])
	v.append(y_val[i])
	#v.append(metadata.loc[i,"uncertainty"])

	bets.loc[i,:]=v
#print(bets.loc[0,:])
#print(bets)

#Betting
print("\nNow let's bet!")

#print("*** Kelly criterion ***\n")
#print("1) Lori's implementation")
u.kelly_bet(bets)
#print("2) Raphael's code")
#bets_streak = u.Bets(method='better_odds')
#roi = bets_streak.roi(list(probs[:,0]), list(metadata.loc[:,"p1_odd"]), list(metadata.loc[:,"p2_odd"]), list(y_val))
#print('\n\tROI : {}%\n'.format(round(roi,4)*100))

print("\nComparison1 - always betting on predicted winner by the odds")
u.trivial_bet2(bets)
print("\nComparison 2 - always betting on predicted winner by the model")
u.trivial_bet(bets)




