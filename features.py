import pandas as pd
from datetime import datetime
import pandasql as ps

df = pd.read_csv('useful_data.csv', sep=',')
#test query
#print(ps.sqldf("select * from df where best_of=1"))

#so now from df I need to build for each match the previous statistics of the 2 players
