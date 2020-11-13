# ATP_predictions
MALIS Project

The scripts of the Data_Creation folder output the "final_data.csv" file with historical data and odds for each ATP match in the decade 2010-2019 with enough past statistics.

  ### Models to be implemented after data preparation
  - SVM
  - Logistic Regression
  - Neural Networks
  - etc.

### Notes 
- work on data cleansing to see when a feature is practically useless if not even harmful (ex 100% break points converted);
- RR matches are counted as the same round, so they cannot be used for other RR matches of the same tourney (and some errors may be occurring in the odds merging when 2 matches between the same players have happened in an ATP Finals tournament);
- no data before 1/1/2010 has been taken into account: this might be a further development of the work, as matches from early years would surely benefit from an analysis of e.g. 2005-2010 historical data.
  


