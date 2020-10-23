import pandas as pd
from datetime import datetime
import pandasql as ps
import random

#so now from df we need to build for each match the previous statistics of the 2 players and other relevant features
def create_pre_match_features(row):
	"""
	It reads the players' names and the date and builds the feature vector for the upcoming match
	"""

	#print("creating pre-match features for {} vs {}".format(row["winner_name"],row["loser_name"]))

	#vector to be populated and appended to the matches DataFrame
	v=[]

	date=row["tourney_date"]

	#player1
	player1=random.choice([row["winner_name"],row["loser_name"]])
	player1_data,p1_wins=retrieve_player_stats(player1,date)

	#player2
	if player1==row["winner_name"]:
		player2=row["loser_name"]
	else:
		player2=row["winner_name"]
	player2_data,p2_wins=retrieve_player_stats(player2,date)

	if p1_wins==False or p2_wins==False:
		return False
	else:
		#we have sufficient data

		#now we build the feature vector for the match of the given row
		v.append(player1)
		v.append(player2)
		#rank difference
		v.append(row["winner_rank"]-row["loser_rank"])
		v.append(player1_data["first_serve_p"]-player2_data["first_serve_p"])
		v.append(player1_data["first_serve_w"]-player2_data["first_serve_w"])
		v.append(player1_data["second_serve_w"]-player2_data["second_serve_w"])
		v.append(player1_data["service_points_w"]-player2_data["service_points_w"])
		v.append(player1_data["return_points_w"]-player2_data["return_points_w"])
		v.append(player1_data["total_points_w"]-player2_data["total_points_w"])
		v.append(p1_wins-p2_wins)
		v.append(player1_data["aces_per_game"]-player2_data["aces_per_game"])
		v.append(player1_data["df_per_game"]-player2_data["df_per_game"])
		v.append(player1_data["conceded_bp_pg"]-player2_data["conceded_bp_pg"])
		v.append(player1_data["saved_bp_perc"]-player2_data["saved_bp_perc"])
		v.append(player1_data["obtained_bp_pg"]-player2_data["obtained_bp_pg"])
		v.append(player1_data["converted_bp_perc"]-player2_data["converted_bp_perc"])

		#'complete' feature
		v.append(round(player1_data["service_points_w"]*player1_data["return_points_w"]-player2_data["service_points_w"]*player2_data["return_points_w"],4))
		#'serveadv' feature
		v.append((player1_data["service_points_w"]-player2_data["return_points_w"])-(player2_data["service_points_w"]-player1_data["return_points_w"]))
		#h2h
		p1_h2h_wins=ps.sqldf("SELECT COUNT(*) as p1w FROM df WHERE winner_name=='{}' AND loser_name=='{}'".format(player1,player2)).loc[0,"p1w"]
		p2_h2h_wins=ps.sqldf("SELECT COUNT(*) as p2w FROM df WHERE winner_name=='{}' AND loser_name=='{}'".format(player2,player1)).loc[0,"p2w"]
		v.append(round((p1_h2h_wins/(p1_h2h_wins+p2_h2h_wins))-(p2_h2h_wins/(p1_h2h_wins+p2_h2h_wins)),4))

		#winner
		if player1==row["winner_name"]:
			v.append(0)
		else:
			v.append(1)

		return v

def retrieve_player_stats(player,date):
	"""
	It returns a dictionary with the historical statistics of a player up to the given date
	"""
	#print("Retrieving data about {}...".format(player))
	matches_num=[0,0]
	player_stats={
	#first element is for wins, second for losses
	"first_serve_p":[0,0],
	"first_serve_w":[0,0],
	"second_serve_w":[0,0],
	"service_points_w":[0,0],
	"return_points_w":[0,0],
	"total_points_w":[0,0],
	"aces_per_game":[0,0],
	"df_per_game":[0,0],
	"conceded_bp_pg":[0,0],
	"saved_bp_perc":[0,0],
	"obtained_bp_pg":[0,0],
	"converted_bp_perc":[0,0]
	}

	#won matches data
	matches_num[0], player_stats["first_serve_p"][0], player_stats["first_serve_w"][0], player_stats["second_serve_w"][0], player_stats["service_points_w"][0], \
	player_stats["return_points_w"][0], player_stats["total_points_w"][0],player_stats["aces_per_game"][0],player_stats["df_per_game"][0], player_stats["conceded_bp_pg"][0], \
	player_stats["saved_bp_perc"][0], player_stats["obtained_bp_pg"][0], player_stats["converted_bp_perc"][0]=ps.sqldf("SELECT COUNT (*) as tot_matches_won, AVG(w_fs) as afs, \
		AVG(w_w1s) as wfs, AVG(w_w2s) as wss, AVG(w_wsp) as w_wsp, AVG(w_wrp) as w_wrp, AVG(w_tpw) as w_tpw, AVG(w_apg) as w_apg, AVG(w_dfpg) as w_dfpg, AVG(w_bppg) as w_bppg, \
		AVG(w_bps) as w_bps, AVG(l_bppg) as l_bppg, AVG(l_bps) as l_bps from df WHERE winner_name == '{}' AND tourney_date<'{}'".format(player,date)).loc[0, \
		["tot_matches_won","afs","wfs","wss","w_wsp","w_wrp","w_tpw","w_apg","w_dfpg","w_bppg","w_bps","l_bppg", "l_bps"]]


	#lost matches data
	#n_lost=ps.sqldf("SELECT COUNT (*) as tot_matches_lost from df WHERE loser_name == '{}' AND tourney_date<'{}'".format(player,date))["tot_matches_lost"][0]
	matches_num[1], player_stats["first_serve_p"][1], player_stats["first_serve_w"][1], player_stats["second_serve_w"][1], player_stats["service_points_w"][1], \
	player_stats["return_points_w"][1], player_stats["total_points_w"][1],player_stats["aces_per_game"][1],player_stats["df_per_game"][1], player_stats["conceded_bp_pg"][1], \
	player_stats["saved_bp_perc"][1], player_stats["obtained_bp_pg"][1], player_stats["converted_bp_perc"][1]=ps.sqldf("SELECT COUNT (*) as tot_matches_lost, AVG(l_fs) as afs, \
		AVG(l_w1s) as wfs, AVG(l_w2s) as wss, AVG(l_wsp) as wsp, AVG(l_wrp) as wrp, AVG(l_tpw) as tpw, \
		AVG(l_apg) as apg, AVG(l_dfpg) as dfpg, AVG(l_bppg) as l_bppg, AVG(l_bps) as l_bps, AVG(w_bppg) as w_bppg, AVG(w_bps) as w_bps from df WHERE loser_name == '{}' AND \
		tourney_date<'{}'".format(player,date)).loc[0,["tot_matches_lost","afs","wfs","wss","wsp","wrp","tpw","apg","dfpg","l_bppg","l_bps","w_bppg", "w_bps"]]

	#print("{} has {} wins and {} losses from 1/1/2010 until now".format(player,matches_num[0],matches_num[1]))
	if matches_num[0]+matches_num[1]<10:
		return False,False

	#fix break points converted
	for it in range(len(player_stats["converted_bp_perc"])):
		player_stats["converted_bp_perc"][it]=1-player_stats["converted_bp_perc"][it]

	#overall weighted averages
	for k in player_stats.keys():
		player_stats[k]=round((player_stats[k][0]*matches_num[0]+player_stats[k][1]*matches_num[1])/(matches_num[0]+matches_num[1]),4)

	#print(player_stats)

	return player_stats,round(matches_num[0]/(matches_num[0]+matches_num[1]),4)

if __name__ == '__main__':

	df = pd.read_csv('useful_data.csv', sep=',')
	column_names=["p1","p2","rank","fs","w1sp","w2sp","wsp","wrp","tpw","tmw","aces","df","bpc","bps","bpo","bpw","complete","serveadv","h2h","winner"]
	matches=pd.DataFrame(columns=column_names) #df to be filled

	#print(df)

	#let's suppose that the first 1000 matches have too few past data to be counted
	count=0
	for i in range(1000,df.shape[0]):
		print(i)
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
	 TO DO: scale normal features to unit variance
	 TO DO: think of how to treat non-normal features
	 TO DO: evaluate each feature's UNCERTAINTY and see when a feature is practically useless if not even harmful (ex 100% break points converted)

	 TO DO: time discounting: last matches played must count more!
	 TO DO: use only common opponents data?
	 TO DO: how to treat surface? Weight on other matches?
	 TO DO: probably better to keep the 'tournament round' feature, map it into a number and use it to consider also matches of the same torunament (date is always the same!)
	 TO DO: fatigue modeling (num. games  played from start of tournament/last two weeks?)
	"""




