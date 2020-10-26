import pandas as pd
import glob, os
from datetime import datetime
import re

#read and concatenate dataframes
#df = pd.concat(map(pd.read_csv, glob.glob(os.path.join('', "Data/*.csv"))),ignore_index=True)
#I put it this way as in the other way they were not ordered by year
df1=pd.read_csv("Data/atp_matches_2010.csv", sep=',')
df2=pd.read_csv("Data/atp_matches_2011.csv", sep=',')
df3=pd.read_csv("Data/atp_matches_2012.csv", sep=',')
df4=pd.read_csv("Data/atp_matches_2013.csv", sep=',')
df5=pd.read_csv("Data/atp_matches_2014.csv", sep=',')
df6=pd.read_csv("Data/atp_matches_2015.csv", sep=',')
df7=pd.read_csv("Data/atp_matches_2016.csv", sep=',')
df8=pd.read_csv("Data/atp_matches_2017.csv", sep=',')
df9=pd.read_csv("Data/atp_matches_2018.csv", sep=',')
df10=pd.read_csv("Data/atp_matches_2019.csv", sep=',')

df = pd.concat([df1, df2, df3, df4, df5, df6, df7, df8, df9, df10],ignore_index=True)

#drop unwanted features
to_drop=["tourney_id","draw_size","tourney_level","match_num","minutes","winner_seed","winner_entry","winner_ht","winner_ioc","loser_seed","loser_entry","loser_ht", \
         "loser_ioc","round","winner_rank_points","loser_rank_points"]
#NOTE some features may be taken into account later (ex tourney level, round, ...)
useful_data=df.copy(deep=True)
useful_data=useful_data.drop(to_drop, axis=1) 
#drop incomplete rows
useful_data=useful_data.dropna(axis=0,how="any") #check

#CATEGORICAL FEATURES MAPPING
#surface mapping
surface_codes = {'Hard':0, 'Clay':1, 'Grass':2} #map surface as categorical value
useful_data["surface"] = df["surface"].map(surface_codes)
#tourney date mapping
useful_data["tourney_date"]=df["tourney_date"].map(lambda d: datetime.strptime(str(d), '%Y%m%d'))

#******
#TO DO: how to count score? Num of sets won by the loser? Or just num of games played (evaluated later)?
#******
#tournament_round mapping
round_codes={"RR":0, "R128":1, "R64":2, "R32":3, "R16":4, "QF":5, "SF":6, "F":7}
#PROBLEM: like this, Round Robin (RR) matches are counted as the same round, so I cannot use previous RR matches for another RR match!
useful_data["round"]=df["round"].map(round_codes)

#best_of mapping
setnum_codes = {3:0, 5:1}
useful_data=useful_data.replace({"best_of": setnum_codes})
#hand mapping
hand_codes={"R":0,"L":1}
useful_data["winner_hand"] = df["winner_hand"].map(hand_codes)
useful_data["loser_hand"] = df["loser_hand"].map(hand_codes)

#delete rows with too low (probably wrong) service points values
#print(useful_data.query('w_svpt == 0'))
#print(len(useful_data))
useful_data = useful_data[useful_data.w_svpt > 10]
useful_data = useful_data[useful_data.l_svpt > 10]
useful_data = useful_data[useful_data.w_1stIn > 10]
useful_data = useful_data[useful_data.l_1stIn > 10]
#print(len(useful_data))

#evaluate first serve % and create new column
useful_data['w_fs'] = useful_data.apply(lambda row : int(row['w_1stIn'])/int(row['w_svpt']), axis = 1)
useful_data['l_fs'] = useful_data.apply(lambda row : int(row['l_1stIn'])/int(row['l_svpt']), axis = 1) 
#evaluate first serve won %
useful_data['w_w1s'] = useful_data.apply(lambda row : int(row['w_1stWon'])/int(row['w_1stIn']), axis = 1)
useful_data['l_w1s'] = useful_data.apply(lambda row : int(row['l_1stWon'])/int(row['l_1stIn']), axis = 1)
#evaluate second serve won %
useful_data['w_w2s'] = useful_data.apply(lambda row : int(row['w_2ndWon'])/int(row['w_svpt']-row['w_1stIn']), axis = 1)
useful_data['l_w2s'] = useful_data.apply(lambda row : int(row['l_2ndWon'])/int(row['l_svpt']-row['l_1stIn']), axis = 1)
#overall winning on serve percentage
useful_data['w_wsp'] = useful_data.apply(lambda row : (int(row['w_1stWon'])+int(row['w_2ndWon']))/int(row["w_svpt"]), axis = 1)
useful_data['l_wsp'] = useful_data.apply(lambda row : (int(row['l_1stWon'])+int(row['l_2ndWon']))/int(row["l_svpt"]), axis = 1)
#overall winning on return percentage
useful_data['w_wrp'] = useful_data.apply(lambda row : (1-row["l_wsp"]), axis = 1)
useful_data['l_wrp'] = useful_data.apply(lambda row : (1-row["w_wsp"]), axis = 1)
#overall points won percentage
useful_data["w_tpw"]=useful_data.apply(lambda row: (row["w_svpt"]*row["w_wsp"]+row["l_svpt"]*row["w_wrp"])/(row["w_svpt"]+row["l_svpt"]), axis=1)
useful_data["l_tpw"]=useful_data.apply(lambda row: (row["l_svpt"]*row["l_wsp"]+row["w_svpt"]*row["l_wrp"])/(row["w_svpt"]+row["l_svpt"]), axis=1)
#aces per game
useful_data["w_apg"]=useful_data.apply(lambda row: row["w_ace"]/row["w_SvGms"], axis=1)
useful_data["l_apg"]=useful_data.apply(lambda row: row["l_ace"]/row["l_SvGms"], axis=1)
#double faults per game
useful_data["w_dfpg"]=useful_data.apply(lambda row: row["w_df"]/row["w_SvGms"], axis=1)
useful_data["l_dfpg"]=useful_data.apply(lambda row: row["l_df"]/row["l_SvGms"], axis=1)
#break points per game
useful_data["w_bppg"]=useful_data.apply(lambda row: row["w_bpFaced"]/row["w_SvGms"], axis=1)
useful_data["l_bppg"]=useful_data.apply(lambda row: row["l_bpFaced"]/row["l_SvGms"], axis=1)
#break points saved
def breaks_w(row):
    if row["w_bpFaced"]>0:
        return row["w_bpSaved"]/row["w_bpFaced"]
    else:
        return 1
    
def breaks_l(row):
    if row["l_bpFaced"]>0:
        return row["l_bpSaved"]/row["l_bpFaced"]
    else:
        return 1    
useful_data["w_bps"]=useful_data.apply(breaks_w, axis=1)
useful_data["l_bps"]=useful_data.apply(breaks_l, axis=1)
#total games played
useful_data["tot_games"]=useful_data.apply(lambda row: row["w_SvGms"]+row["l_SvGms"], axis=1)

#it would be cool to have winners, unforced errors and net approaches won, as they represent the playing style of a player;
#but currently we don't have 'em in these datasets

#remove columns used to evaluate percentages
to_drop2=['w_1stIn','l_1stIn','w_svpt','l_svpt','w_1stWon','l_1stWon','w_2ndWon','l_2ndWon',"w_SvGms","l_SvGms",'w_bpFaced','l_bpFaced',\
         "w_bpSaved","l_bpSaved","w_ace","l_ace","w_df","l_df"]
useful_data=useful_data.drop(to_drop2, axis=1) 


#print(useful_data.dtypes)
#useful_data
useful_data.head(2)
useful_data.to_csv(r'useful_data.csv', index = False)