# ATP_predictions
MALIS Project

## Things to do before passing to ML Algorithms implementation:
  	- CHECK: common opponents implementation
	- CHECK: time weighting implementation
	- CHECK: uncertainty implementation
	- CHECK: tourney round implementation (+ NOTE: RR matches are counted as the same round, so they cannot be used for other RR matches of the same tourney)
	- CHECK: surface weighting implementation (correlations used as weights obtained in the script surfaces.py)
	- CHECK: fatigue modeling (% difference in num. games played from start of tournament) [NOTE: for now, we did not implement INJURY modeling, as it is quite difficult and did not prove to have a consistent impact on the results]

	- TO DO: scale normal features to unit variance
	- TO DO: think of how to treat non-normal features
	- TO DO: work on data cleansing to see when a feature is practically useless if not even harmful (ex 100% break points converted)
  
  ### Models to be implemented after data preparation
  - SVM
  - Logistic Regression
  - Neural Networks
  - etc.
  
  #### Note: all the BETTING part will be added after a first simple binary classification basis has been implemented
