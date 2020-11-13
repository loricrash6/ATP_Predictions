##Workflow

The creation of the "final_data.csv" file happened with the following procedure.

1) From the raw data of each match, create through the script "data_creator.py" the meaningful statistics for each match that will serve our purpose. 
This outputs the file "useful_data.csv".

2) Through the "features.py" script, for each match a vector containing the differences in the historical performances of the two players is created.
Comments on the script explain the adopted strategies. This outputs the "matches.csv" file.
(NOTE This part makes also use of "surfaces.py" for surface weighting)

3) At this point, we just need to add the odds of each match, which are taken from another bunch of files. The script "odds.py" does so and produces "odds.csv".
An intermediate passage is executed with "tourney_mapping.py" on "matches.csv": the tournament name is mapped to an id so that the join with "odds.csv" can be easily done.
Script "data_merging.py" does so and produces the ultimate data needed for our ML implementation in the file "final_data.csv".
