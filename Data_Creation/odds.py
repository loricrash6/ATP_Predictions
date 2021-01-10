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

#read betting odds in a dataframe

matches=pd.read_csv('matches.csv', sep=',') 
#data=pd.read_csv('useful_data.csv', sep=',')

fp = open("tournaments.json", 'r')
d = json.load(fp)
fp.close()

dict_names=d["dict_names"]

odds=pd.DataFrame(columns=["Location","Tournament","Winner","Loser","B365W","B365L","year","tourney_id"])
for y in range(2010,2020,1):
#for y in range(2020,2021,1):
	if y<2013:
		o=pd.read_excel("Betting_data/"+str(y)+".xls")
	else:
		o=pd.read_excel("Betting_data/"+str(y)+".xlsx")
	o=o[["Location","Tournament","Winner","Loser","B365W","B365L"]]
	o['year'] = str(y)

	#tourney id mapping
	o['tourney_id']=math.nan
	for i in range(o.shape[0]):
		for k in dict_names.keys():
			if o.loc[i]["Tournament"] in dict_names[k]:
				o.loc[i,"tourney_id"]=int(k)


	odds=pd.concat([odds,o],ignore_index=True)

odds.to_csv("odds.csv",index=False)

#we have odds.csv
#now we join odds and matches

#print(odds.shape[0])
#print(data.shape[0]) #a little bigger (26765 vs 26328: for some matches we do not have odds, apparently)





