import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn import metrics
import matplotlib.pyplot as plt

def log_regr(df_start,features,training_years,validation_years,cut_train,cut_val,save_weights):

	to_sel=features+["p1","p2","uncertainty","winner","p1_odd","p2_odd","year","tourney_id"]
	df=df_start[to_sel]

	#train
	train=df[(df["year"].isin(training_years))] 
	#extract label column
	train=train.sort_values(by=["uncertainty"])[0:round(train.shape[0]*cut_train)].reset_index(drop=True)
	y_train = train["winner"]
	train_tonorm=train.drop(["p1","p2","p1_odd","p2_odd","winner","uncertainty","year","tourney_id"], axis=1)
	train_norm = train_tonorm/train_tonorm.std(numeric_only=True)
	if "h2h" in train_norm.columns:
		train_norm["h2h"]=train["h2h"] #direct did not need standardization

	#validation 
	val=df[(df["year"].isin(validation_years))].reset_index(drop=True)
	val=val.sort_values(by=["uncertainty"])[0:round(val.shape[0]*cut_val)].reset_index(drop=True)
	y_val = val["winner"]
	metadata=val[["p1","p2","p1_odd","p2_odd","uncertainty","year"]]
	val_tonorm=val.drop(["p1","p2","p1_odd","p2_odd","winner","uncertainty","year","tourney_id"], axis=1)
	val_norm = val_tonorm/val_tonorm.std(numeric_only=True)
	if "h2h" in val_norm.columns:
		val_norm["h2h"]=val["h2h"] #h2h did not need standardization

	#LOGISTIC REGRESSION
	clf = linear_model.LogisticRegression(C=0.2).fit(train_norm, y_train)
	y_hat_train=clf.predict(train_norm)
	#print("Training accuracy:",metrics.accuracy_score(y_train, y_hat_train))
	y_hat_val=clf.predict(val_norm)
	#print("Validation accuracy:",metrics.accuracy_score(y_val, y_hat_val))

	y_val_prob=clf.predict_proba(val_norm)

	coeff=list(clf.coef_.reshape([len(features)])) #coefficients

	#dataframe for ROI/logloss evaluation
	columns=["p0","p1","prob0","prob1","odd0","odd1","label"]#,"uncertainty"]
	bets=pd.DataFrame(columns=columns)

	for i in range(y_val_prob.shape[0]):
		v=[]
		v.append(metadata.loc[i,"p1"])
		v.append(metadata.loc[i,"p2"])
		v.append(y_val_prob[i,0])
		v.append(y_val_prob[i,1])
		v.append(metadata.loc[i,"p1_odd"])
		v.append(metadata.loc[i,"p2_odd"])
		v.append(y_val[i])
		#v.append(metadata.loc[i,"uncertainty"])

		bets.loc[i,:]=v

	labels=y_val.to_numpy().reshape(y_val.shape[0],1)
	pred=(bets.loc[:,["prob0","prob1"]]).to_numpy()

	loss=metrics.log_loss(labels,pred)

	if save_weights==False:
		return loss,bets
	else:
		return loss,bets,coeff

def kelly_bet(bets):
	# KELLY CRITERION BETTING
	x=range(bets.shape[0])
	y=[]
	b=100
	q=10 #max bet size
	n_bets=[0,0,0] #placed, won, lost
	print("Starting with: {}€".format(b))
	print("\n...betting ongoing with Kelly criterion...\n")
	for i in range(bets.shape[0]):

		#print(bets.loc[i,:])

		#print("\n Currently betting on {} vs {}:\n\t- ML estimated probabilites: {} vs {}\n\t- B365 odds: {} vs {}".\
		#	format(bets.loc[i,"p0"],bets.loc[i,"p1"],bets.loc[i,"prob0"],bets.loc[i,"prob1"],bets.loc[i,"odd0"],bets.loc[i,"odd1"]))

		#evaluate implied probabilities from odds
		p0_ip=1/bets.loc[i,"odd0"]
		p1_ip=1/bets.loc[i,"odd1"]

		#print("P_bookies - player 0 to win: {}, player 1 to win: {}".format(p0_ip,p1_ip))

		s0=0
		if bets.loc[i,"prob0"]>(p0_ip) and bets.loc[i,"prob0"]>0.5:
			s0=float(round(q*((bets.loc[i,"prob0"]*bets.loc[i,"odd0"]-1)/(bets.loc[i,"odd0"]-1)),2))
		
		s1=0
		if bets.loc[i,"prob1"]>(p1_ip) and bets.loc[i,"prob1"]>0.5:
			s1=float(round(q*((bets.loc[i,"prob1"]*bets.loc[i,"odd1"]-1)/(bets.loc[i,"odd1"]-1)),2))
		
		
		if s0<=0:
			s0=0
		elif s0>0 and s0<2: #min quota: 2€
			s0=2
		if s1<=0:
			s1=0
		elif s1>0 and s1<2:
			s1=2
		

		earning=0

		if s0>0:
			#we bet on player 0
			n_bets[0]+=1
			print("Betting {}€ on p0 ({}): pbettor={} vs pbookie={}".format(s0,bets.loc[i,"p0"],bets.loc[i,"prob0"],p0_ip))
			b=b-s0
			print("Temporary budget: {}".format(b))

			if bets.loc[i,"label"]==1:
				#we lost
				#b=b-s0
				print("lost {}€ on this one...".format(s0))
				n_bets[2]+=1

			elif bets.loc[i,"label"]==0:
				#we won
				earning=float(s0)*float(bets.loc[i,"odd0"])
				b=b+earning
				print("yeah bitch: earning {}*{}={}€".format(s0,bets.loc[i,"odd0"],(s0)*bets.loc[i,"odd0"]))
				n_bets[1]+=1

		elif s1>0:
			#we bet on player 1
			n_bets[0]+=1
			print("Betting {}€ on p1 ({}): pbettor={} vs pbookie={}".format(s1,bets.loc[i,"p1"],bets.loc[i,"prob1"],p1_ip))
			b=b-s1
			print("Temporary budget: {}".format(b))

			if bets.loc[i,"label"]==0:
				#we lost
				print("lost {}€ on this one...".format(s1))
				n_bets[2]+=1

			elif bets.loc[i,"label"]==1:
				#we won
				earning=float(s1)*float(bets.loc[i,"odd1"])
				b=b+earning
				print("yeah bitch: earning {}*{}={}€".format(s1,bets.loc[i,"odd1"],(s1)*bets.loc[i,"odd1"]))
				n_bets[1]+=1
		else:
			print("too close to call...")
			#pass

		print("New budget: {}€\n".format(b))
		b=round(b,2)
		y.append(b)

		if earning>50:
			print("*** BIG WIN ALERT! ***")
			#print(bets.loc[i,:])
			#if s0>0:
			#	print("Betted {} on p0, won {}x{}={}".format(s0,s0,bets.loc[i,"odd0"],earning))
			#else:
			#	print("Betted {} on p1, won {}x{}={}".format(s1,s1,bets.loc[i,"odd1"],earning))


	print("\n***\n")
	print("After {} matches at disposal: \n\t-bets placed: {}\n\t-won: {}\n\t-lost: {}\n".format(bets.shape[0], n_bets[0], n_bets[1], n_bets[2]))
	print("Final budget: {}€".format(round(b,2)))
	print("ROI: {}%\n".format(round((b-100)/100,4)*100))
	print("\n***\n")

	fig=plt.figure()
	plt.plot(x,y,'b')
	#plt.legend(loc='upper right',fontsize=10)
	plt.xlabel("Bet no.",fontsize=10)
	plt.ylabel("Budget",fontsize=10)
	plt.title("Budget evolution during betting streak", fontsize=15)
	plt.xticks(fontsize=10)
	plt.yticks(fontsize=10)
	#plt.ylim(0,0.2)
	#plt.xlim(-1,1)
	plt.grid()
	plt.show()
	