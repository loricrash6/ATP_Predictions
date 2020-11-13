import pandas as pd
from datetime import datetime
import pandasql as ps
import random
import numpy as np
import math
import time
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn import metrics
from sklearn.svm import SVC
import pickle
import json

#MERGE MATCHES.CSV AND ODDS.CSV TO PRODUCE FINAL DATA FILE!

matches=pd.read_csv('matches_mapped.csv', sep=',') 
matches=matches.drop(["date","tourney"], axis=1)
odds=pd.read_csv("odds.csv",sep=",")

final=pd.DataFrame(columns=["p1","p2","rank","fs","w1sp","w2sp","wsp","wrp","tpw","aces","df","bpc","bps",\
	"bpo","bpw","tmw","complete","serveadv","h2h","fatigue","uncertainty","winner","tourney_id","year","p1_odd","p2_odd"])

for i in range(matches.shape[0]):
	row=matches.loc[i,:]
	year=row["year"]
	tourney=row["tourney_id"] #tourney id mapped also in matches having used tourney_mapping.py!

	p1_odd=math.nan
	p2_odd=math.nan

	odds_year=odds[(odds["year"]==year) & (odds["tourney_id"]==tourney)]
	odds_year=odds_year.reset_index(drop=True)
	
	for j in range(odds_year.shape[0]):
		row2=odds_year.loc[j,:]
		
		# we have to add the betting odds
		winner_surname=row2["Winner"].replace("-"," ").split(" ")[0]
		loser_surname=row2["Loser"].replace("-"," ").split(" ")[0]
		winner_surname2=row2["Winner"].replace("-"," ").split(" ")[1] #in cases like "del Potro"
		loser_surname2=row2["Loser"].replace("-"," ").split(" ")[1]

		if ((winner_surname in row["p1"] or winner_surname2 in row["p1"]) and ((loser_surname in row["p2"]\
		 or loser_surname2 in row["p2"]))):
			
			p1_odd=row2["B365W"]
			p2_odd=row2["B365L"]

		elif ((winner_surname in row["p2"] or winner_surname2 in row["p2"]) and ((loser_surname in row["p1"]\
			 or loser_surname2 in row["p1"]))):
			p2_odd=row2["B365W"]
			p1_odd=row2["B365L"]
	
	row=list(row)
	row.extend([p1_odd,p2_odd])
	final.loc[i,:]=row

final=final.dropna(axis=0,how="any") #drop matches for which we do not have the odds
#print(final)
final.to_csv('final_data.csv',index=False)