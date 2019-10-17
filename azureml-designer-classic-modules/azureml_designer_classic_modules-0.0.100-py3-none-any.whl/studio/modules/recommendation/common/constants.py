# These indexes are used for input datasets of train recommendation modules
# and score recommendation modules. The dataset columns are assumed to
# correspond to user identifies, item identifies, and rating identifies
USER_COLUMN_INDEX = 0
ITEM_COLUMN_INDEX = 1
RATING_COLUMN_INDEX = 2

# These column names are used for the output data of score recommendation
# modules and input data of evaluate recommendation module. For rating prediction task,
# data column names must be User, Item and Rating respectively. For Item
# recommendation task, data column names must be User, Item 1, Item 2, Item 3 ... or
# User, Item 1, Rating 1, Item 2, Rating 2, Item 3, Rating 3 ....
PREDICTED_RATING_COLUMN = "Rating"
PREDICTED_USER_COLUMN = "User"
PREDICTED_ITEM_COLUMN = "Item"
RECOMMENDED_ITEM_COLUMN_PREFIX = "Item"
RECOMMENDED_RATING_COLUMN_PREFIX = "Rating"
PREDICTION_COLUMNS = [PREDICTED_USER_COLUMN, PREDICTED_ITEM_COLUMN, PREDICTED_RATING_COLUMN]

# These column names are used for the output data of evaluate recommendation module.
MAE_COLUMN = "MAE"
RMSE_COLUMN = "RMSE"
NDCG_COLUMN = "NDCG"
