# ATP_predictions
MALIS Project

The scripts of the Data_Creation folder output the "final.csv" file with historical data and odds for each ATP match in the decade 2010-2019 with enough past statistics.

The file "tests.py" tries to do some feature selection with logistic regression using forward addition and implements a first ideal betting tentative.
Results are, for now, very bad,

  ## Models to be implemented 
  - SVM
  - Logistic Regression
  - Neural Networks
  - etc.
  
### Notes 
- work on data cleansing to see when a feature is practically useless if not even harmful (ex 100% break points converted): problem - it should be done before the creation of final.csv;
- RR matches are counted as the same round, so they cannot be used for other RR matches of the same tourney (and some errors may be occurring in the odds merging when 2 matches between the same players have happened in an ATP Finals tournament);
- surface_weighting of the current final.csv file was based on a previous run; values might not be exactly accurate: in the future we'll need to re-run surface.py on our defined training set and re-create the final.csv file with the correct weights, but this shouldn't affect heavily our classification performances for now.
  


