import numpy as np
import pandas as pd
from azureml.studio.common.error import MoreThanOneRatingError, ErrorMapping
from azureml.studio.modules.recommendation.common.constants import PREDICTED_USER_COLUMN, \
    RECOMMENDED_ITEM_COLUMN_PREFIX, USER_COLUMN_INDEX, ITEM_COLUMN_INDEX, RATING_COLUMN_INDEX


# This method is used to build column names for item recommendation data. Can be used in
# score recommender modules and evaluate recommender module. The item recommendation data
# column names must be User, Item 1, Item 2, Item 3 ... or User, Item 1, Rating 1, Item 2,
# Rating 2, Item 3, Rating 3 ....
def build_item_recommendation_column_names(max_recommended_item_count):
    """Return column names for result DataFrame of item recommendation task."""
    if max_recommended_item_count <= 0:
        raise ValueError("Maximum number of items to recommend to a user must greater than zero")
    column_names = [PREDICTED_USER_COLUMN]
    for i in range(max_recommended_item_count):
        column_names.append(f"{RECOMMENDED_ITEM_COLUMN_PREFIX} {i + 1}")
    return column_names


def get_user_column_name(df: pd.DataFrame):
    return df.columns[USER_COLUMN_INDEX]


def get_item_column_name(df: pd.DataFrame):
    return df.columns[ITEM_COLUMN_INDEX]


def get_rating_column_name(df: pd.DataFrame):
    return df.columns[RATING_COLUMN_INDEX]


def preprocess_triples(df: pd.DataFrame, dataset_name=None):
    """Preprocess user-item-rating triples.

    For user/item ids, the preprocess includes NaN/None values drop and converting to string type.
    For ratings, the preprocess includes NaN, Inf values drop and check duplicate ratings.
    :param df: the pd.DataFrame object with 3 columns, corresponding to (user,item,rating) triples
    :param dataset_name: str
    :return: pd.DataFrame
    """
    df = preprocess_tuples(df, drop_duplicate=False)
    # check duplicate user-item pairs
    user_column = get_user_column_name(df)
    item_column = get_item_column_name(df)
    duplicate_boolean = df.duplicated(subset=[user_column, item_column])
    if duplicate_boolean.any():
        duplicate_sample = df[duplicate_boolean].iloc[0, :]
        ErrorMapping.throw(
            MoreThanOneRatingError(user=duplicate_sample[user_column], item=duplicate_sample[item_column],
                                   dataset=dataset_name))

    rating_column = df.columns[RATING_COLUMN_INDEX]
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=[rating_column]).reset_index(drop=True)
    return df


def preprocess_tuples(df: pd.DataFrame, drop_duplicate=True):
    """Preprocess user-item tuples.

    The preprocess includes dropping NaN/None values, converting user and item ids to string type,
    dropping duplicate user-item pairs.
    :param df: the pd.DataFrame object with 2 columns, corresponding to (user,item) tuples
    :param drop_duplicate: whether to drop duplicate (user,item) tuples
    :return: pd.DataFrame
    """
    user_column, item_column = df.columns[[USER_COLUMN_INDEX, ITEM_COLUMN_INDEX]]
    df = preprocess_id_columns(df, column_subset=[user_column, item_column])
    if drop_duplicate:
        df = df.drop_duplicates(subset=[user_column, item_column])
    return df


def preprocess_id_columns(df: pd.DataFrame, column_subset: list):
    """Preprocess user/item id columns. The preprocess includes NaN/None values drop and converting to string type."""
    df = df.dropna(subset=column_subset).reset_index(drop=True)
    df[column_subset] = df[column_subset].astype(str)

    return df
