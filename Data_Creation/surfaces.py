import pandas as pd
from datetime import datetime
import pandasql as ps
import random
import numpy as np
import math
import time

if __name__ == '__main__':

	df = pd.read_csv('useful_data.csv', sep=',')
	df["year"]=df.apply(lambda row: int(row["tourney_date"][0:4]),axis=1)
	win=list(ps.sqldf("SELECT DISTINCT winner_name as win FROM df WHERE year<2018").loc[:,"win"])
	los=list(ps.sqldf("SELECT DISTINCT loser_name as los FROM df WHERE year<2018").loc[:,"los"])
	#print(len(win))
	#print(len(los))
	win.extend(los)
	players=set(win)
	N=len(players)

	column_names=["player","hard","clay","grass"] #we'll store each player win % for each surface
	surf=pd.DataFrame(columns=column_names)

	count=0
	for p in players:
		wh=df[(df["winner_name"]==p) & (df["surface"]==float(0))].shape[0]
		wc=df[(df["winner_name"]==p) & (df["surface"]==float(1))].shape[0]
		wg=df[(df["winner_name"]==p) & (df["surface"]==float(2))].shape[0]
		lh=df[(df["loser_name"]==p) & (df["surface"]==float(0))].shape[0]
		lc=df[(df["loser_name"]==p) & (df["surface"]==float(1))].shape[0]
		lg=df[(df["loser_name"]==p) & (df["surface"]==float(2))].shape[0]

		if (wh+lh)>0:
			ph=wh/(wh+lh)
		else:
			ph=float('nan')

		if (wc+lc)>0:
			pc=wc/(wc+lc)
		else:
			pc=float('nan')

		if (wg+lg)>0:
			pg=wg/(wg+lg)
		else:
			pg=float('nan')

		v=[]
		v.append(p)
		v.append(ph)
		v.append(pc)
		v.append(pg)

		surf.loc[count]=v
		count+=1

	
	#means and stedvs of columns
	m=[surf["hard"].mean(skipna=True),surf["clay"].mean(skipna=True),surf["grass"].mean(skipna=True)]
	s=[surf["hard"].std(skipna=True),surf["clay"].std(skipna=True),surf["grass"].std(skipna=True)]

	#drop rows with nan, not really useful
	#surf=surf.dropna(axis=0,how="any")
	# corrected: keep nan and see each time if columns i and j are nan or not

	print("Means: {}".format(m))
	print("Stdevs: {}".format(s))
	
	c1,c2,c3=0,0,0
	c=[0,0,0]
	for i in range(surf.shape[0]):
		if ((np.isnan(surf.iloc[i]["hard"])) or (np.isnan(surf.iloc[i]["clay"]))):
			pass
		else:
			c1+=(surf.iloc[i]["hard"]-m[0])*(surf.iloc[i]["clay"]-m[1])
			c[0]+=1
		if ((np.isnan(surf.iloc[i]["hard"])) or (np.isnan(surf.iloc[i]["grass"]))):
			pass
		else:
			c2+=(surf.iloc[i]["hard"]-m[0])*(surf.iloc[i]["grass"]-m[2])
			c[1]+=1
		if ((np.isnan(surf.iloc[i]["grass"])) or (np.isnan(surf.iloc[i]["clay"]))):
			pass
		else:
			c3+=(surf.iloc[i]["clay"]-m[1])*(surf.iloc[i]["grass"]-m[2])
			c[2]+=1

	rho1=c1/((c[0]-1)*s[0]*s[1])
	rho2=c2/((c[1]-1)*s[0]*s[2])
	rho3=c3/((c[2]-1)*s[1]*s[2])
	#rho1=c1/((surf.shape[0]-1)*s[0]*s[1])
	#rho2=c2/((surf.shape[0]-1)*s[0]*s[2])
	#rho3=c3/((surf.shape[0]-1)*s[1]*s[2])
	print(rho1,rho2,rho3)

	# RESULTS: 0,34 - 0,40 - 0,30 