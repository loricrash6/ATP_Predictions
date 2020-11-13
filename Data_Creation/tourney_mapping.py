import pandas as pd
import math
import json
from datetime import datetime

df = pd.read_csv('matches.csv', sep=',')
#map tournament and year into matches.csv (for the merging with odds.csv!)

fp = open("tournaments.json", 'r')
d = json.load(fp)
fp.close()

dict_names=d["dict_names"]

df["tourney_id"]=math.nan

for i in range(df.shape[0]):
	df.loc[i,"year"]=df.loc[i,"date"][0:4]
	for k in dict_names.keys():
		if df.loc[i]["tourney"] in dict_names[k]:
			df.loc[i,"tourney_id"]=int(k)

	#note: Brisbane and other tournaments in some year began in late December: shift to following year
	month=df.loc[i,"date"][5:7]
	if int(month)==12:
		df.loc[i,"year"]=str(int(df.loc[i,"date"][0:4])+1)

#print(df)
df.to_csv('matches_mapped.csv',index=False)

#NOTE not mapped matches: Olympics (London and Rio) + Davis Cup - not gonna be used



