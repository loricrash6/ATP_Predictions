# ATP_predictions
MALIS Project

## Things to do before passing to ML Algorithms implementation:
- CHECK: common opponents implementation
- CHECK: time weighting implementation
- CHECK uncertainty implementation
- CHECK: tourney round implementation (+ NOTE: RR matches are counted as the same round, so they cannot be used for other RR matches of the ame tourney)

- TO DO: how to treat surface? Weight on other matches? Simple categorical feature? Consider only matches of the same surface (greatly reduces training data though..)
- TO DO: fatigue modeling (num. games played from start of tournament/last two weeks?)

- TO DO: scale normal features to unit variance
- TO DO: think of how to treat non-normal features
- TO DO: work on data cleansing to see when a feature is practically useless if not even harmful (ex 100% break points converted)
