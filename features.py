import pandas as pd
from datetime import datetime
import pandasql as ps
import random
import numpy as np
import math
import time

f=0.8 #constant for time discount
s_disc=np.matrix([[1, 0.34, 0.4],[0.34,1,0.3],[0.4, 0.3, 1]]) #surface discount weights (Hard-Clay, Hard-Green, Clay-Green) derived from surfaces.py

def time_discount(row):
	f=0.8
	diff=row["year_diff"]
	i=f**diff

	if f<=i:
		return f
	else:
		return i

def surface_weighting(row):
	s=row.s_ref
	s2=row.s

	return s_disc[int(s),int(s2)]
	
#so now from df we need to build for each match the previous statistics of the 2 players and other relevant features
def create_pre_match_features(row):
	"""
	It reads the players' names and the date and builds the feature vector for the upcoming match
	"""

	v=[] #vector to be populated
	

	#print("creating pre-match features for {} vs {}".format(row["winner_name"],row["loser_name"]))

	date=row["tourney_date"]
	r=row["round"]
	sur=row["surface"]
	#player1 (randomly assigned!)
	player1=random.choice([row["winner_name"],row["loser_name"]])
	#player2
	if player1==row["winner_name"]:
		player2=row["loser_name"]
	else:
		player2=row["winner_name"]

	v.append(player1)
	v.append(player2)
	#rank difference
	v.append(row["winner_rank"]-row["loser_rank"])

	#the function retrieve_player_stats should return a dataframe with the average stats of player against each common opponent with the other player
	avg_p1=retrieve_player_stats(player1,player2,date,r,sur)
	avg_p2=retrieve_player_stats(player2,player1,date,r,sur)

	#overall uncertainty of the data at disposal for the past matches of p1 and p2 against their common opponents
	s=0
	if avg_p1.shape[0]>0:
		for i in range(avg_p1.shape[0]):
			s+=(avg_p1.iloc[i]["uncertainty"]*avg_p2.iloc[i]["uncertainty"])
			#print("Uncertainty for {}: {} x {} ".format(avg_p2.iloc[i]["opponent"],avg_p1.iloc[i]["uncertainty"],avg_p2.iloc[i]["uncertainty"]))
		u=1/s #u is the overall uncertainty of our feature vector for the match!
	
	if ((avg_p1.shape[0]>0) and (avg_p2.shape[0]>0)):
		#p1
		stats_p1=list(avg_p1.mean(axis=0,numeric_only=True)[0:13])
		stats_p2=list(avg_p2.mean(axis=0,numeric_only=True)[0:13])

		diffs=list(np.subtract(stats_p1,stats_p2))

		v.extend(diffs)

		v.append(round(stats_p1[3]*stats_p1[4]-stats_p2[3]*stats_p2[4],4)) #complete
		v.append((stats_p1[3]-stats_p2[4])-(stats_p2[3]-stats_p1[4])) #serveadv
		#h2h
		h2h_1=df[((df["winner_name"]==player1) & (df["loser_name"]==player2)) & ((df["tourney_date"]<date) | (\
			(df["tourney_date"]==date) & (df["round"]<r)))].shape[0]
		h2h_2=df[((df["winner_name"]==player2) & (df["loser_name"]==player1)) & ((df["tourney_date"]<date) | (\
			(df["tourney_date"]==date) & (df["round"]<r)))].shape[0]
		#h2h=df[(((df["winner_name"]==player2) & (df["loser_name"]==player1)) | ((df["winner_name"]==player1) & (df["loser_name"]==player2))) \
		#& (df["tourney_date"]<datetime.strptime(date,"%Y-%m-%d"))] #no round implemented in this try
		if (h2h_1+h2h_2)>0:
			v.append(round((h2h_1/(h2h_1+h2h_2))-(h2h_2/(h2h_1+h2h_2)),4))
		else:
			v.append(0) #dummy value

		#fatigue feature
		# NOTE we don't have the data of each match, but only the starting date of the tournament;
		# therefore, the only thing that can be done is counting the num. of games played since the beginning of the tournament and give a % difference btw the 2 players.
		# This does not take into account the exact distance in days of previous matches from the current one, nor matches of the previous tournament,
		# but from our perspective it seems quite impossible to do differently.
		tourney_p1=df[(((df["winner_name"]==player1) | (df["loser_name"]==player1)) & ((df["tourney_date"]==date) & (df["round"]<r)))]
		p1_games=tourney_p1["tot_games"].sum()
		tourney_p2=df[(((df["winner_name"]==player2) | (df["loser_name"]==player2)) & ((df["tourney_date"]==date) & (df["round"]<r)))]
		p2_games=tourney_p2["tot_games"].sum()
		
		v.append(round((p1_games/(p1_games+p2_games))-(p2_games/(p1_games+p2_games)),4))

		v.append(u) #append uncertainty!

		if player1==row["winner_name"]:
			v.append(0)
		else:
			v.append(1)

		#print(v)
		return v
	else:
		return False
		 
def retrieve_player_stats(player1,player2,date,r,sur):
	"""
	It returns a dictionary with the historical statistics of a player up to the given date for matches against common opponents shared with player2
	"""
	#COMMON OPPONENTS APPROACH
	#print("Retrieving data about {} with respect to {} for matches before {}...".format(player1,player2,date))
	
	#TIME DISCOUNTING
	#we try to give higher weight to most recent matches
	#to do so, we select the rows of interest AND the difference (in years) from the present date which will serve as weight
	
	####
	#df["tourney_date"]=pd.to_datetime(df["tourney_date"]) #to allow date comparison MOVED AT THE BEGINNING
	#games played by player1
	g1=df[((df["winner_name"]==player1) | (df["loser_name"]==player1)) & ((df["tourney_date"]<date) | (\
		(df["tourney_date"]==date) & (df["round"]<r)))]
	
	#o1=def1.loc[def1["winner_name"]==player1]
	ow=list(g1.loc[(df.winner_name==player1, 'loser_name')].values[:])
	ol=list(g1.loc[(df.loser_name==player1, 'winner_name') ].values[:])
	o1=set(ow+ol) #player 1 opponents

	#games played by player2
	g2=df[((df["winner_name"]==player2) | (df["loser_name"]==player2)) & ((df["tourney_date"]<date) | (\
		(df["tourney_date"]==date) & (df["round"]<r)))]
	#o1=def1.loc[def1["winner_name"]==player1]
	ow=list(g2.loc[(df.winner_name==player2, 'loser_name')].values[:])
	ol=list(g2.loc[(df.loser_name==player2, 'winner_name') ].values[:])
	o2=set(ow+ol) #player 2 opponents

	#list of common opponents 
	co=[x for x in o1 if x in o2]
	#print(co)
	
	column_names=["fs","w1sp","w2sp","wsp","wrp","tpw","aces","df","bpc","bps","bpo","bpw","tmw","uncertainty","opponent",]
	averages=pd.DataFrame(columns=column_names) #df to be filled with one row per opponent
	
	count=0
	#now evaluate average statistics of player1 wrt to each common opponent, then we'll do the average
	for o in co:
		#print("Matches of {} vs {}...".format(player1,o))
		tot_w=0
		tot_l=0

		#select matches of player 1 vs opponent o
		m=df[((((df["winner_name"]==player1) & (df["loser_name"]==o))) | ((df["winner_name"]==o) & (df["loser_name"]==player1))) & \
		((df["tourney_date"]<date) | ((df["tourney_date"]==date) & (df["round"]<r)))]
		if m.shape[0] > 0:
			#we have min 2 past matches against opponent o
			#won matches
			w=m[m["winner_name"]==player1].loc[:,['w_fs', 'w_w1s', 'w_w2s', 'w_wsp', 'w_wrp', 'w_tpw', 'w_apg', 'w_dfpg', 'w_bppg', 'w_bps', 'l_bppg', 'l_bps', 'loser_name',\
			'tourney_date','surface']].rename(columns={'w_fs':'fs','w_w1s':'w1s','w_w2s':'w2s','w_wsp':'wsp','w_wrp':'wrp','w_tpw':'tpw','w_apg':'apg','w_dfpg':'dfpg','w_bppg':'bppg',\
			'w_bps':'bps','l_bppg':'bpo','l_bps':'l_bps','loser_name':'opponent', 'tourney_date':'date','surface':'s'})
			if w.shape[0]>0:
				w["bpc"]=w.apply(lambda row: 1-row["l_bps"],axis=1)
				#set year difference param.
				w["year_diff"]=w.apply(lambda row: int(date.year-row["date"].year), axis=1)

				tot_w=w.shape[0]
			w=w.drop("l_bps", axis=1)

			#lost matches
			l=m[m["loser_name"]==player1].loc[:,['l_fs', 'l_w1s', 'l_w2s', 'l_wsp', 'l_wrp', 'l_tpw', 'l_apg', 'l_dfpg', 'l_bppg', 'l_bps', 'w_bppg', 'w_bps', 'winner_name',\
			'tourney_date','surface']].rename(columns={'l_fs':'fs','l_w1s':'w1s','l_w2s':'w2s','l_wsp':'wsp','l_wrp':'wrp','l_tpw':'tpw','l_apg':'apg','l_dfpg':'dfpg','l_bppg':'bppg',\
			'l_bps':'bps','w_bppg':'bpo','w_bps':'w_bps','winner_name':'opponent','tourney_date':'date','surface':'s'})
			if l.shape[0]>0:
				l["bpc"]=l.apply(lambda row: 1-row["w_bps"],axis=1)
				
				l["year_diff"]=l.apply(lambda row: int(date.year-row["date"].year), axis=1)

				tot_l=l.shape[0]
				
			l=l.drop("w_bps", axis=1)

			#join the two datframes, so that we have all the matches
			j = pd.concat([w, l],sort=False)
			#weight for surface
			j["s_ref"]=j.apply(lambda row: sur,axis=1) #reference surface of match under study
			j["s_w"]=j.apply(surface_weighting,axis=1) #surface weight of each previous match
			#j=j.drop("s", axis=1)

			#assign weight which decreases as year_diff is higher
			j["discounting"]=j.apply(time_discount,axis=1)
			#further multiply time weights by surface weights
			j["discounting"]=j.apply(lambda row: row["discounting"]*row["s_w"],axis=1)
			#j=j.drop("s_ref", axis=1)
			#j=j.drop("s_w", axis=1)
			#j=j.drop("year_diff", axis=1)

			tot_weights=j["discounting"].sum()
			#normalize weights to sum to 1
			j["discounting"]=j.apply(lambda row: row["discounting"]/j["discounting"].sum(),axis=1)
			#print(j)
			#weight all the matches for the discounting param
			#hence, multiply columns 0-11 for column "discounting"
			j.update(j.iloc[:, 0:11].mul(j.discounting, 0))
			j["bpc"]=j.apply(lambda row: row["bpc"]*row["discounting"],axis=1)
			#now to have the weghted average of each stat, sum all the column
			avg=list(j.sum(axis=0,numeric_only=True)[0:12])
			avg.append(tot_w/(tot_w+tot_l)) #append % of matches won against o
			avg.append(1/tot_weights) #add uncertainty 
			avg.append(o)
    		
    		#NOW we have data for past matches of player1 against common opponent o
			#add to dataframe, go to next one
			averages.loc[count]=avg
			count+=1
			
			
	#at the end of the loop, return the dataframe
	#in the outer function, compute general uncertainties with data of the two players combined, 
	#then evaluate average statistics btw all the common opponents for each player - finally, build the ultimate feature vector
	#print(averages)
	return averages

	
if __name__ == '__main__':

	df = pd.read_csv('useful_data.csv', sep=',')
	df["tourney_date"]=pd.to_datetime(df["tourney_date"]) #to allow date comparison
	#print(df.shape)
	column_names=["p1","p2","rank","fs","w1sp","w2sp","wsp","wrp","tpw","aces","df","bpc","bps","bpo","bpw","tmw","complete","serveadv","h2h","fatigue","uncertainty","winner"]
	#NOTE: probably we'll need to add an "uncertainty" column
	matches=pd.DataFrame(columns=column_names) #df to be filled with one row for each match

	#print(df)

	#let's suppose (at beginning for simplicity) that the first 10000 matches have too few past data to be counted
	count=0
	for i in range(10019,10020):#df.shape[0]):
		#print(i)
		row=df.loc[i,:]

		feat_vector=create_pre_match_features(row)

		if feat_vector!=False:
			matches.loc[count]=feat_vector
			count+=1
			print("Match added to dataframe!\n")
		else:
			print("Not enough data for these players! Match skipped...\n")

	print(matches)
	"""
	CHECK: common opponents implementation
	CHECK: time weighting implementation
	CHECK: uncertainty implementation
	CHECK: tourney round implementation (+ NOTE: RR matches are counted as the same round, so they cannot be used for other RR matches of the same tourney)
	CHECK: surface weighting implementation (correlations used as weights obtained in the script surfaces.py)
	CHECK: fatigue modeling (% difference in num. games played from start of tournament)

	NOTE: for now, we did not implement INJURY modeling, as it is quite difficult and did not prove to have a consistent impact on the results
 	
 	**********

	TO DO: scale normal features to unit variance
	TO DO: think of how to treat non-normal features
	TO DO: work on data cleansing to see when a feature is practically useless if not even harmful (ex 100% break points converted)
	"""