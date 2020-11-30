import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn import metrics

import test_utils as t

df_start = pd.read_csv('final.csv', sep=',')

df_start=df_start[["p1","p2","rank","fs","w1sp","w2sp","wsp","wrp","tpw","aces","df","bpc","bps","bpo","bpw","tmw","complete","serveadv","h2h","fatigue","uncertainty","winner","p1_odd","p2_odd","year","tourney_id"]]
list_features=["fs","w1sp","w2sp","wsp","wrp","tpw","aces","df","bpc","bps","bpo","bpw","tmw","complete","serveadv","h2h","fatigue"] #no rank!
#Taking only one feature for prediction
#df=df[["p1","p2","serveadv","uncertainty","winner","p1_odd","p2_odd","year","tourney_id"]]

#we need to order features for the progressive insertion
x=[]
y=[]
f=[]
fb=[]
list2=list_features.copy()
overall_best=[]
overall_best_log=100 #fake init

while len(f)<len(list_features):

	#will keep value of the result adding the best feature
	best_metric=0
	best_loss=100 #fake init
	print("\n***\nNum. features: {}".format(len(f)))
	print("Feature list right now: ")
	print(*f,sep=',')

	for candidate_f in list2:
		if candidate_f not in f:
			print("Considering the addition of {}".format(candidate_f))
			
			test_f=f+[candidate_f] #temporary set of features

			loss, bets=t.log_regr(df_start,test_f,[2010,2011,2012,2013,2014],[2015,2016],0.2,0.5,False)
			print("Log loss would be {}".format(loss))

			if loss<best_loss:
				print("For now, it's the best!")
				best_loss=loss
				best_metric=candidate_f

	print("Adding metric {}".format(best_metric))
	f.append(best_metric)
	list2.remove(best_metric)

	if best_loss<overall_best_log:
		overall_best_log=best_loss
		overall_best=f.copy()
		print("*** Overall best feature set improved ***")

	print("Added! No. features = {} of the {} total".format(len(f),len(list_features)))

	x.append(len(f))
	y.append(best_loss)

#from previous trial
#overall_best=['tpw','tmw','h2h','bpw','fs','df','serveadv','complete','aces','bpo','bps','bpc','w1sp']

print("Finished! Below you find the deducted optimal feature set for the problem.")
print(*overall_best,sep=',')

print("Let's evaluate performance on the validation set...")
all_loss, all_bets=t.log_regr(df_start,list_features,[2010,2011,2012,2013,2014,2015,2016],[2018,2017],0.2,0.5,False) #using all features (except rank)
sel_loss, sel_bets, sel_weights=t.log_regr(df_start,overall_best,[2010,2011,2012,2013,2014,2015,2016],[2018,2017],0.2,0.5,True) #using selected feature set
print("Log loss with all features: {}".format(all_loss))
print("Log loss with selected feature set: {}".format(sel_loss))
"""
PLOT LOG. REGR. WEIGHTS
fig=plt.figure()
plt.bar(range(0,len(overall_best)),sel_weights,tick_label=overall_best)
#plt.legend(loc='upper right',fontsize=10)
plt.xlabel("Feature",fontsize=10)
plt.ylabel("Weight",fontsize=10)
plt.title("Weights assigned to final feature set", fontsize=15)
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)
#plt.ylim(0,0.2)
#plt.xlim(-1,1)
plt.grid()
plt.show()
"""
"""
PLOT FEATURE SELECTION EVOLUTION
fig=plt.figure()
plt.plot(x,y,'b')
#plt.legend(loc='upper right',fontsize=10)
plt.xlabel("No. of features taken",fontsize=10)
plt.ylabel("Log-loss",fontsize=10)
plt.title("Forward selection", fontsize=15)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
#plt.ylim(0,0.2)
#plt.xlim(-1,1)
plt.grid()
plt.show()
"""

#ROI evaluation
t.kelly_bet(sel_bets)

"""
PLOTS to show that RANK feature (used alone) gives predictions with very different distribution of probabilities 
wrt to the betting odds implied probabilities - instead, Serveadv gives very similar result --> DO NOT USE RANK!
bets["p0_implied"]=bets.apply(lambda row: 1/row["odd0"], axis=1)

fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Horizontally stacked subplots')

y=bets["prob0"]
ax1.hist(y, density=False, bins=20)
ax1.set_xlabel("P(player 1 win) [%]",fontsize=10)
ax1.set_ylabel("density",fontsize=10)
ax1.set_title("Feature: SERVEADV", fontsize=15)
ax1.set_ylim([0,800])
ax1.grid()

y=bets["p0_implied"]
plt.hist(y, density=False, bins=20)
ax2.set_xlabel("P(player 1 win) [%]",fontsize=10)
ax2.set_ylabel("density",fontsize=10)
ax2.set_title("Implied probabilities", fontsize=15)
ax2.set_ylim([0,800])
ax2.grid()
plt.show()
"""
