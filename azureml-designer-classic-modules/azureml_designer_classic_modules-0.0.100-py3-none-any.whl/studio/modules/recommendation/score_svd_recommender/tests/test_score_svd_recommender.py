import math
import pytest
import pickle
import os
import pandas as pd
import numpy as np
import azureml.studio.common.error as error_setting
from azureml.studio.modules.recommendation.score_svd_recommender.score_svd_recommender import \
    RecommenderPredictionKind, ScoreSVDRecommenderModule, RecommendedItemSelection
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.recommendation.common.recommender_utils import get_item_column_name, get_user_column_name, \
    build_item_recommendation_column_names, preprocess_tuples, preprocess_id_columns
from azureml.studio.modules.recommendation.common.base_recommender import BaseRecommender


def default_entry_params():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    learner_path = os.path.join(script_dir, 'input', 'movie_rating_svd_model.pkl')
    with open(learner_path, 'rb') as f:
        learner = pickle.load(f)
    params_dict = {
        'test_data': None,
        'training_data': None,
        'learner': learner,
        'prediction_kind': RecommenderPredictionKind.ItemRecommendation,
        'recommended_item_selection': RecommendedItemSelection.FromRatedItems,
        'max_recommended_item_count': 5,
        'min_recommendation_pool_size': 2,
        'return_ratings': False
    }
    return params_dict


def _gen_invalid_learner():
    class InvalidLearner(BaseRecommender):
        def __init__(self):
            super().__init__()

        def train(self, training_data_df):
            pass

        def predict(self, test_data_df):
            pass

        def recommend(self, users, max_recommended_items_count, return_ratings, included_items=None,
                      excluded_items=None):
            pass

    learner = InvalidLearner()
    entry_params = default_entry_params()
    entry_params['learner'] = learner
    test_data = [[23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)']]
    test_data = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['test_data'] = test_data
    exp_error = error_setting.InvalidLearnerError
    exp_msg = "Learner \"Trained SVD recommendation\" has invalid type."
    return entry_params, exp_error, exp_msg


def _gen_null_learner():
    entry_params = default_entry_params()
    entry_params['learner'] = None
    exp_error = error_setting.NullOrEmptyError
    exp_msg = "Input \"Trained SVD recommendation\" is null or empty."
    return entry_params, exp_error, exp_msg


def _gen_null_test_data():
    entry_params = default_entry_params()
    exp_error = error_setting.NullOrEmptyError
    exp_msg = "Input \"Dataset to score\" is null or empty."
    return entry_params, exp_error, exp_msg


def _gen_empty_test_data():
    entry_params = default_entry_params()
    entry_params['test_data'] = DataTable(pd.DataFrame({}))
    exp_error = error_setting.TooFewRowsInDatasetError
    exp_msg = r"Number of rows in input dataset \"Dataset to score\" is 0, " \
              r"less than allowed minimum of 1 row\(s\)."
    return entry_params, exp_error, exp_msg


def _gen_null_training_data_for_unrated_item_recommendation():
    entry_params = default_entry_params()
    test_data_dict = {'user': [1, 2, 3]}
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data_dict))
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    exp_error = error_setting.NullOrEmptyError
    exp_msg = "Input \"Training data\" is null or empty."
    return entry_params, exp_error, exp_msg


def _gen_empty_training_data_for_unrated_item_recommendation():
    entry_params = default_entry_params()
    test_data_dict = {'user': [1, 2, 3]}
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data_dict))
    entry_params['training_data'] = DataTable(pd.DataFrame({}))
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    exp_error = error_setting.TooFewRowsInDatasetError
    exp_msg = r"Number of rows in input dataset \"Training data\" is 0, " \
              r"less than allowed minimum of 1 row\(s\)."
    return entry_params, exp_error, exp_msg


def _gen_too_few_columns_for_rating_prediction():
    entry_params = default_entry_params()
    test_data_dict = {'user': [1, 2, 3]}
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data_dict))
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    exp_error = error_setting.TooFewColumnsInDatasetError
    exp_msg = r"Number of columns in input dataset \"Dataset to score\" is less than allowed minimum of 2 column\(s\)."
    return entry_params, exp_error, exp_msg


def _gen_too_many_columns_for_rating_prediction():
    entry_params = default_entry_params()
    test_data_dict = {'user': [1, 2, 3], 'item': [4, 5, 6], 'rating': [7, 8, 9], 'extra_col': [10, 11, 12]}
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data_dict))
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    exp_error = error_setting.UnexpectedNumberOfColumnsError
    exp_msg = "Unexpected number of columns in the dataset \"Dataset to score\"."
    return entry_params, exp_error, exp_msg


def _gen_invalid_column_number_for_item_recommendation(recommended_item_selection):
    entry_params = default_entry_params()
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = recommended_item_selection
    exp_error = None
    exp_msg = None
    test_data_dict = None
    if recommended_item_selection == RecommendedItemSelection.FromRatedItems:
        test_data_dict = {'user': [1, 2, 3]}
        exp_error = error_setting.TooFewColumnsInDatasetError
        exp_msg = r"Number of columns in input dataset \"Dataset to score\" is " \
                  r"less than allowed minimum of 2 column\(s\)."
    elif recommended_item_selection == RecommendedItemSelection.FromAllItems:
        test_data_dict = {'user': [1, 2, 3], 'item': [4, 5, 6], 'rating': [7, 8, 9], 'extra_col': [10, 11, 12]}
        exp_error = error_setting.UnexpectedNumberOfColumnsError
        exp_msg = "Unexpected number of columns in the dataset \"Dataset to score\"."
    elif recommended_item_selection == RecommendedItemSelection.FromUnratedItems:
        test_data_dict = {'user': [1, 2, 3]}
        training_data_dict = {'user': [4, 5, 6]}
        training_data = DataTable(pd.DataFrame(training_data_dict))
        entry_params['training_data'] = training_data
        exp_error = error_setting.TooFewColumnsInDatasetError
        exp_msg = r"Number of columns in input dataset \"Training data\" is less than allowed minimum of 2 column\(s\)."

    entry_params['test_data'] = DataTable(pd.DataFrame(test_data_dict))
    return entry_params, exp_error, exp_msg


@pytest.mark.parametrize('entry_params,exp_error,exp_msg', [
    _gen_invalid_learner(),
    _gen_null_learner(),
    _gen_null_test_data(),
    _gen_empty_test_data(),
    _gen_null_training_data_for_unrated_item_recommendation(),
    _gen_empty_training_data_for_unrated_item_recommendation(),
    _gen_too_few_columns_for_rating_prediction(),
    _gen_too_many_columns_for_rating_prediction(),
    _gen_invalid_column_number_for_item_recommendation(RecommendedItemSelection.FromRatedItems),
    _gen_invalid_column_number_for_item_recommendation(RecommendedItemSelection.FromAllItems),
    _gen_invalid_column_number_for_item_recommendation(RecommendedItemSelection.FromUnratedItems),
])
def test_error_case(entry_params, exp_error, exp_msg):
    with pytest.raises(expected_exception=exp_error, match=exp_msg):
        ScoreSVDRecommenderModule.run(**entry_params)


def test_multi_type_id_data():
    entry_params = default_entry_params()
    test_data = {'User': [True, 1, 'a'], 'Item': [5.2, 'c', False]}
    test_data = DataTable(pd.DataFrame(test_data))
    entry_params['test_data'] = test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    ScoreSVDRecommenderModule.run(**entry_params)


@pytest.fixture
def imported_test_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(script_dir, 'input', 'movie_ratings_test_small.csv')
    test_data = DataTable(pd.read_csv(test_file_path))
    return test_data


@pytest.fixture
def imported_training_data():
    train_set_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', 'movie_ratings_train.csv')
    training_data_df = pd.read_csv(train_set_path)
    training_data = DataTable(training_data_df)
    return training_data


def test_rating_prediction_with_duplicate_data():
    entry_params = default_entry_params()
    test_data = [[23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)']]
    test_data = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['test_data'] = test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 1


def test_recommend_rated_items_with_duplicate_data():
    entry_params = default_entry_params()
    test_data = [[23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)']]
    test_data = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['test_data'] = test_data
    entry_params['min_recommendation_pool_size'] = 1
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    ref_res_df = pd.DataFrame([['23963', 'J. Edgar (2011)', np.nan, np.nan, np.nan, np.nan]],
                              columns=build_item_recommendation_column_names(
                                  entry_params['max_recommended_item_count']))
    assert res.data_frame.equals(ref_res_df)
    entry_params['min_recommendation_pool_size'] = 2
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 0


def test_recommend_all_items_with_duplicate_data():
    entry_params = default_entry_params()
    test_data = [[23963], [23963], [23963]]
    test_data = DataTable(pd.DataFrame(test_data, columns=['user']))
    entry_params['test_data'] = test_data
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromAllItems
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 1


def test_recommend_unrated_items_with_duplicate_data(imported_training_data):
    entry_params = default_entry_params()
    test_data = [[23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)'], [23963, 'J. Edgar (2011)']]
    test_data = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['test_data'] = test_data
    entry_params['training_data'] = imported_training_data
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 1


def test_nan_value_data(imported_training_data):
    # verify not throw when recommend rated items
    entry_params = default_entry_params()
    test_data = [[np.nan, 'Taken 2 (2012)'], [21936, np.nan], [np.nan, np.nan]]
    test_data = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['test_data'] = test_data
    entry_params['max_recommended_item_count'] = 1
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 0
    # verify not throw when recommend all items
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromAllItems
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 1
    # verify not throw when recommend unrated items
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    entry_params['training_data'] = imported_training_data
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 1
    # verify not throw for rating prediction
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    res = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert res.number_of_rows == 0


def test_cold_start_items(imported_training_data):
    entry_params = default_entry_params()
    # verify recommend rated items for cold start items
    cold_start_test_data = [['6820', 'cold_start_item'], ['6820', 'Riddick (2013)']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user', 'item']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['max_recommended_item_count'] = 2
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert set(scored_data.data_frame.values[0][1:]) == {'cold_start_item', 'Riddick (2013)'}

    # verify recommend unrated items for cold start items
    cold_start_test_data = [['6820', 'cold_start_item']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user', 'item']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    entry_params['training_data'] = imported_training_data
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == cold_start_test_data.number_of_rows
    assert scored_data.number_of_columns == entry_params['max_recommended_item_count'] + 1

    # verify rating prediction for cold start user
    cold_start_test_data = [['6820', 'cold_start_item'], ['6820', 'Riddick (2013)']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user', 'item']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == cold_start_test_data.number_of_rows


def test_cold_start_users(imported_training_data):
    entry_params = default_entry_params()
    # verify recommend rated items for cold start user
    cold_start_test_data = [['cold_start_user', 'Primer (2004)'], ['cold_start_user', 'Now You See Me (2013)']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user', 'item']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['max_recommended_item_count'] = 2
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert set(scored_data.data_frame.values[0][1:]) == {'Primer (2004)', 'Now You See Me (2013)'}

    # verify recommend all items for cold start user
    cold_start_test_data = [['cold_start_user']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromAllItems
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == cold_start_test_data.number_of_rows
    assert scored_data.number_of_columns == entry_params['max_recommended_item_count'] + 1

    # verify recommend unrated items for cold start user
    cold_start_test_data = [['cold_start_user', 'Primer (2004)']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user', 'item']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    entry_params['training_data'] = imported_training_data
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == cold_start_test_data.number_of_rows
    assert scored_data.number_of_columns == entry_params['max_recommended_item_count'] + 1

    # verify rating prediction for cold start user
    cold_start_test_data = [['cold_start_user_1', 'Primer (2004)'], ['cold_start_user_2', 'Now You See Me (2013)']]
    cold_start_test_data = DataTable(pd.DataFrame(cold_start_test_data, columns=['user', 'item']))
    entry_params['test_data'] = cold_start_test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == cold_start_test_data.number_of_rows


def test_rating_prediction_with_imported_data(imported_test_data):
    entry_params = default_entry_params()
    entry_params['test_data'] = imported_test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.RatingPrediction
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]

    test_data_df = imported_test_data.data_frame
    user_column = get_user_column_name(test_data_df)
    item_column = get_item_column_name(test_data_df)
    test_data_df = test_data_df.sort_values([user_column, item_column])[[user_column, item_column]].astype(str)

    scored_data_df = scored_data.data_frame
    user_column = get_user_column_name(scored_data_df)
    item_column = get_item_column_name(scored_data_df)
    scored_data_df = scored_data_df.sort_values([user_column, item_column])[[user_column, item_column]].astype(str)
    test_data_df.equals(scored_data_df)
    # verify column names
    assert scored_data.column_names == ['User', 'Item', 'Rating']


def test_recommend_rated_items_with_imported_data(imported_test_data):
    entry_params = default_entry_params()
    entry_params['test_data'] = imported_test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromRatedItems
    entry_params['max_recommended_item_count'] = 5
    entry_params['min_recommendation_pool_size'] = 1
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]

    test_data_df = imported_test_data.data_frame
    user_column = get_user_column_name(test_data_df)
    item_column = get_item_column_name(test_data_df)
    test_data_df = preprocess_tuples(test_data_df)
    # test_data_df = preprocess_user_item_ids(test_data_df)

    test_user_rated_items_group = test_data_df.groupby(by=user_column)
    test_user_rated_items = test_user_rated_items_group[item_column].apply(lambda x: list(x))[
        test_user_rated_items_group.size() >= entry_params['min_recommendation_pool_size']]
    test_user_rated_items = test_user_rated_items.sort_index()
    test_valid_users = test_user_rated_items.index.values
    test_user_rated_items = test_user_rated_items.values

    scored_data_df = scored_data.data_frame
    user_column = get_user_column_name(scored_data_df)
    scored_data_df = scored_data_df.sort_values(user_column)
    scored_valid_users = scored_data_df[user_column].values
    scored_recommend_items = scored_data_df.drop(columns=user_column).values
    scored_recommend_items = [[item for item in items if not pd.isnull(item)] for items in scored_recommend_items]

    # verify column names
    assert scored_data.column_names == ['User', 'Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
    # verify valid users are as expected
    assert np.array_equal(test_valid_users, scored_valid_users)
    # verify recommend items are contained in rated items
    boolean_list = [set(scored_recommend_items[i]).issubset(set(test_user_rated_items[i])) for i in
                    range(len(scored_valid_users))]
    assert all(boolean_list)


def test_recommend_all_items_with_imported_data(imported_test_data):
    entry_params = default_entry_params()
    entry_params['test_data'] = imported_test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromAllItems
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]

    test_data_df = imported_test_data.data_frame
    user_column = get_user_column_name(test_data_df)
    test_data_df = preprocess_id_columns(test_data_df, column_subset=[user_column])
    test_users = np.sort(test_data_df[user_column].unique())

    scored_data_df = scored_data.data_frame
    user_column = get_user_column_name(scored_data_df)
    scored_users = np.sort(scored_data_df[user_column].values)

    # verify column names
    assert scored_data.column_names == ['User', 'Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
    # verify scored users are the same as test users
    assert np.array_equal(test_users, scored_users)
    # verify recommended item counts
    assert scored_data.number_of_columns == entry_params['max_recommended_item_count'] + 1


def test_recommend_unrated_items_with_imported_data(imported_test_data, imported_training_data):
    entry_params = default_entry_params()
    entry_params['test_data'] = imported_test_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    training_data = imported_training_data
    training_data_df = imported_training_data.data_frame
    entry_params['training_data'] = training_data
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]

    user_column = get_user_column_name(training_data_df)
    item_column = get_item_column_name(training_data_df)
    # training_data_df = preprocess_user_item_ids(training_data_df)
    training_data_df = preprocess_tuples(training_data_df)
    rated_items = training_data_df.groupby(user_column)[item_column].apply(list)

    test_data_df = imported_test_data.data_frame
    user_column = get_user_column_name(test_data_df)
    test_data_df = preprocess_id_columns(test_data_df, column_subset=[user_column]).sort_values([user_column])
    test_users = test_data_df[user_column].unique()
    rated_items = rated_items[test_users].apply(lambda x: [] if type(x) != list and math.isnan(x) else x)

    scored_data_df = scored_data.data_frame
    user_column = get_user_column_name(scored_data_df)
    scored_data_df = scored_data_df.sort_values(user_column)
    scored_users = scored_data_df[user_column].values
    scored_recommended_items = scored_data_df.drop(columns=user_column).values

    # verify column names
    assert scored_data.column_names == ['User', 'Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
    # verify users are as expected
    assert np.array_equal(test_users, scored_users)
    # verify recommended items are not in rated items
    boolean_list = [set(scored_recommended_items[i]).isdisjoint(set(rated_items[test_users[i]])) for i in
                    range(len(test_users))]
    assert all(boolean_list)


def test_recommend_rated_items_with_rating():
    entry_params = default_entry_params()
    test_data = [[4400, 'Dredd (2012)']]
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromRatedItems
    entry_params['max_recommended_item_count'] = 3
    entry_params['min_recommendation_pool_size'] = 1
    entry_params['return_ratings'] = True
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == 1
    # verify column names
    assert scored_data.column_names == ['User', 'Item 1', 'Rating 1', 'Item 2', 'Rating 2', 'Item 3', 'Rating 3']


def test_recommend_all_items_with_rating():
    entry_params = default_entry_params()
    test_data = [[4400, 'Dredd (2012)']]
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromAllItems
    entry_params['max_recommended_item_count'] = 3
    entry_params['return_ratings'] = True
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == 1
    # verify column names
    assert scored_data.column_names == ['User', 'Item 1', 'Rating 1', 'Item 2', 'Rating 2', 'Item 3', 'Rating 3']


def test_recommend_unrated_items_with_rating(imported_training_data):
    entry_params = default_entry_params()
    test_data = [[4400, 'Dredd (2012)']]
    entry_params['test_data'] = DataTable(pd.DataFrame(test_data, columns=['user', 'item']))
    entry_params['training_data'] = imported_training_data
    entry_params['prediction_kind'] = RecommenderPredictionKind.ItemRecommendation
    entry_params['recommended_item_selection'] = RecommendedItemSelection.FromUnratedItems
    entry_params['max_recommended_item_count'] = 1
    entry_params['return_ratings'] = True
    scored_data = ScoreSVDRecommenderModule.run(**entry_params)[0]
    assert scored_data.number_of_rows == 1
    # verify column names
    assert scored_data.column_names == ['User', 'Item 1', 'Rating 1']
