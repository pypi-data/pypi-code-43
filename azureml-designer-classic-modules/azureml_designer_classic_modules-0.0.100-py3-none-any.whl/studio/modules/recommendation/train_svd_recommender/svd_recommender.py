import surprise
import pandas as pd
import numpy as np
from azureml.studio.core.logger import time_profile
from azureml.studio.modules.recommendation.common.recommender_utils import get_user_column_name, get_item_column_name
from azureml.studio.modules.recommendation.common.constants import RATING_COLUMN_INDEX, PREDICTED_USER_COLUMN, \
    RECOMMENDED_ITEM_COLUMN_PREFIX, RECOMMENDED_RATING_COLUMN_PREFIX, PREDICTED_ITEM_COLUMN, PREDICTED_RATING_COLUMN
from azureml.studio.modules.recommendation.common.base_recommender import BaseRecommender


class SVDRecommender(BaseRecommender):
    def __init__(self, num_factors, num_iterations, learning_rate, random_state=0):
        self.model = surprise.SVD(n_factors=num_factors,
                                  n_epochs=num_iterations,
                                  lr_all=learning_rate,
                                  random_state=random_state,
                                  verbose=False)

    @time_profile
    def train(self, training_data: pd.DataFrame, label_column_name: str = None, cv=None):
        """Train SVD Recommendation model with given dataset.

        This method inherits from superclass, the param label_column_name and cv is not useful for recommendation.
        """
        training_dataset = self._build_dataset(training_data)
        # for now, we use bias to compute ratings for cold-start users and items,
        # for details, refer to Surprise libaray source codes.
        self.model.fit(trainset=training_dataset)

    def predict(self, test_data_df: pd.DataFrame):
        """Predict rating for each user-item pair in the test data."""
        user_ids = test_data_df[get_user_column_name(test_data_df)]
        item_ids = test_data_df[get_item_column_name(test_data_df)]
        predictions = [self.model.predict(user_id, item_id).est for user_id, item_id in zip(user_ids, item_ids)]
        result_df = pd.DataFrame({PREDICTED_USER_COLUMN: user_ids,
                                  PREDICTED_ITEM_COLUMN: item_ids,
                                  PREDICTED_RATING_COLUMN: predictions})
        return result_df

    def recommend(self, users, max_recommended_item_count, return_ratings, included_items=None, excluded_items=None):
        """Recommend a list of items for each user.

        This method generates a certain number of recommended items for each user. The candidate items are
        determined by included_items and excluded_items parameters. These parameters are not expected to be
        non-None at the same time. And if they are both None, we consider all items as candidate items for each user.

        :param users: a series of users.
        :param max_recommended_item_count: customize the number of recommended items for each user.
        :param return_ratings: whether including corresponding rating for each recommended item or not.
        :param included_items: defaults to None. If not None, each element in included_items is expected to contain
                candidate items for the corresponding user.
        :param excluded_items: defaults to None. If not None, each element in excluded_items is expected to contain
                items not to be considered for the corresponding user.
        :return: result DataFrame object.
        """
        recommended_items = []
        recommended_item_ratings = []

        if included_items is not None:
            total_items = included_items
        elif excluded_items is not None:
            full_items = set(self.model.trainset._raw2inner_id_items.keys())
            total_items = [list(full_items - set(items)) for items in excluded_items]
        else:
            total_items = [list(self.model.trainset._raw2inner_id_items.keys())] * len(users)
        for target_user, target_items in zip(users, total_items):
            topk_items, topk_ratings = self._recommended_topk_items(target_user, target_items,
                                                                    max_recommended_item_count)
            recommended_items.append(topk_items)
            recommended_item_ratings.append(topk_ratings)
        res_df = SVDRecommender._format_recommend_result(users, recommended_items, recommended_item_ratings,
                                                         max_recommended_item_count, return_ratings)
        return res_df

    @staticmethod
    def _format_recommend_result(users, recommended_items, recommended_item_ratings, max_recommended_item_count,
                                 return_ratings):
        """Format item recommendation result.

        Format of recommendation results based on V1. According to the value of return_ratings, the results contains
        each item ratings or not. For example, if return_ratings is True,
            User    Item 1                          Rating 1    Item 2                              Rating 2
        0   25546   Forrest Gump (1994)             9.03        Schindlers List (1993)              9.21
        1   338     Schindlers List (1993)          9.14        The Shawshank Redemption (1994)     9.23
        2   5118    The Green Mile (1999)           8.95        The Shawshank Redemption (1994)     8.97
        3   931     Schindlers List (1993)          9.91        Saving Private Ryan (1998)          9.98
        4   9749    The Godfather (1972)            9.13        The Shawshank Redemption (1994)     9.31
        5   5050    The Godfather Part II (1974)    8.70        The Godfather (1972)                8.73
        if return_rating is False,
            User    Item 1                  Item 2                              Item 3
        0   25546   Forrest Gump (1994)     The Godfather (1972)                The Dark Knight (2008)
        1   338     Schindlers List (1993)  The Shawshank Redemption (1994)     The Godfather Part II (1974)
        2   21640   The Dark Knight (2008)  Schindlers List (1993)              The Shawshank Redemption (1994)
        3   14829   Il buono il brutto      The Godfather (1972)                Schindlers List (1993)
        4   5118    Pulp Fiction (1994)     The Green Mile (1999)               The Shawshank Redemption (1994)
        5   26515   Gravity (2013)          Inception (2010)                    Il buono il brutto
        :param users: list
        :param recommended_items: list
        :param recommended_item_ratings: list
        :param max_recommended_item_count: int
        :param return_ratings: bool
        :return: DataFrame
        """
        user_df = pd.DataFrame({PREDICTED_USER_COLUMN: users})
        recommended_item_column_names = []
        recommended_item_rating_column_names = []
        reordered_column_names = [PREDICTED_USER_COLUMN]
        for i in range(max_recommended_item_count):
            recommended_item_column = f"{RECOMMENDED_ITEM_COLUMN_PREFIX} {i + 1}"
            recommended_item_column_names.append(recommended_item_column)
            if return_ratings:
                recommended_item_rating_column = f"{RECOMMENDED_RATING_COLUMN_PREFIX} {i + 1}"
                recommended_item_rating_column_names.append(recommended_item_rating_column)
                reordered_column_names.append(recommended_item_column)
                reordered_column_names.append(recommended_item_rating_column)
        recommended_item_df = pd.DataFrame(data=recommended_items, columns=recommended_item_column_names)
        res_df = pd.concat([user_df, recommended_item_df], axis=1)
        if return_ratings:
            recommended_item_rating_df = pd.DataFrame(data=recommended_item_ratings,
                                                      columns=recommended_item_rating_column_names)
            res_df = pd.concat([res_df, recommended_item_rating_df], axis=1)
            res_df = res_df[reordered_column_names]
        return res_df

    def _recommended_topk_items(self, target_user, target_items, max_recommended_item_count):
        ratings = [self.model.predict(target_user, item).est for item in target_items]
        topk_index = np.argsort(ratings)[-max_recommended_item_count:]
        topk_items = [target_items[idx] for idx in topk_index]
        # use np.nan to fill top-k item list with less than k items
        topk_items += [np.nan] * (max_recommended_item_count - len(topk_items))
        topk_ratings = [ratings[idx] for idx in topk_index]
        # use 0 rating to fill top-k rating list with less than k ratings
        topk_ratings += [0] * (max_recommended_item_count - len(topk_ratings))
        return topk_items, topk_ratings

    @staticmethod
    def _build_dataset(df: pd.DataFrame):
        min_rating = df.iloc[:, RATING_COLUMN_INDEX].min()
        max_rating = df.iloc[:, RATING_COLUMN_INDEX].max()
        rating_scale = [min_rating, max_rating]
        training_dataset = surprise.Dataset.load_from_df(df, reader=surprise.reader.Reader(
            rating_scale=rating_scale)).build_full_trainset()
        return training_dataset
