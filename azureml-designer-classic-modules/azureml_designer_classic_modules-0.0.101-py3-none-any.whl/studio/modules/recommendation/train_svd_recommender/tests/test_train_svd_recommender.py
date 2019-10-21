import pandas as pd
import pytest
import os
import numpy as np
import azureml.studio.common.error as error_setting
from azureml.studio.modules.recommendation.train_svd_recommender.train_svd_recommender import TrainSVDRecommenderModule
from azureml.studio.common.datatable.data_table import DataTable


@pytest.fixture
def entry_params():
    params_dict = {
        "num_factors": 200,
        "num_iterations": 10,
        "learning_rate": 0.005
    }
    return params_dict


def test_smoke_test(entry_params):
    dataset = {'user': [2, 5, 1, 2, 3],
               'item': [4, 2, 1, 3, 4],
               'rating': [1, 2, 3, 4, 5]}
    dataset = DataTable(pd.DataFrame(dataset))
    TrainSVDRecommenderModule.run(training_data=dataset, **entry_params)


def test_nan_dataset(entry_params):
    dataset = {'user': [np.nan, 5, 1, 2, 3],
               'item': [4, 2, np.nan, 3, 4],
               'rating': [1, 2, 3, np.nan, 5]}
    dataset = DataTable(pd.DataFrame(dataset))
    TrainSVDRecommenderModule.run(training_data=dataset, **entry_params)


def test_inf_dataset(entry_params):
    dataset = {'user': [1, 2, 3],
               'item': [4, 5, 6],
               'rating': [np.inf, 3, 5]}
    dataset = DataTable(pd.DataFrame(dataset))
    TrainSVDRecommenderModule.run(training_data=dataset, **entry_params)


def test_multi_type_id_dataset(entry_params):
    dataset = {'user': [True, 1, 'bob', 1.84],
               'item': ['The Avengers', False, 6.8, 2],
               'rating': [1, 2, 3, 4]}
    dataset = DataTable(pd.DataFrame(dataset))
    TrainSVDRecommenderModule.run(training_data=dataset, **entry_params)


def test_imported_dataset(entry_params):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, 'input', 'movie_ratings_train.csv')
    dataset = DataTable(pd.read_csv(dataset_path))
    TrainSVDRecommenderModule.run(training_data=dataset, **entry_params)


def _gen_null_dataset():
    dataset = None
    exp_error = error_setting.NullOrEmptyError
    exp_msg = "Input \"Training dataset of user-item-rating triples\" is null or empty."
    return dataset, exp_error, exp_msg


def _gen_invalid_column_number_dataset():
    dataset = {'user': [2, 5, 1, 2, 3],
               'item': [4, 2, 1, 3, 4]}
    dataset = DataTable(pd.DataFrame(dataset))
    exp_error = error_setting.UnexpectedNumberOfColumnsError
    exp_msg = r"In input dataset \"Training dataset of user-item-rating triples\", " \
              r"expected \"3\" column\(s\) but found \"2\" column\(s\) instead."
    return dataset, exp_error, exp_msg


def _gen_invalid_type_rating_dataset():
    dataset = {'user': [2, 5, 1, 2, 3],
               'item': [4, 2, 1, 3, 4],
               'rating': ["1", "2", "3", "4", "5"]}
    dataset = DataTable(pd.DataFrame(dataset))
    exp_error = error_setting.InvalidColumnTypeError
    exp_msg = "Cannot process column \"rating\" of type String. The type is not supported by the module."
    return dataset, exp_error, exp_msg


def _gen_duplicate_rating_dataset():
    dataset = {'user': [2, 5, 1, 2, 3, 3],
               'item': [4, 2, 1, 3, 4, 4],
               'rating': [1, 2, 3, 4, 5, 6]}
    dataset = DataTable(pd.DataFrame(dataset))
    exp_error = error_setting.MoreThanOneRatingError
    exp_msg = "More than one rating for user 3 and item 4 in rating prediction data table."
    return dataset, exp_error, exp_msg


def _gen_empty_dataset():
    dataset = {}
    dataset = DataTable(pd.DataFrame(dataset, columns=['user', 'item', 'rating'], dtype=int))
    exp_error = error_setting.TooFewRowsInDatasetError
    exp_msg = "Number of rows in input dataset \"Training dataset of user-item-rating triples\" is 0, " \
              r"less than allowed minimum of 1 row\(s\)."
    return dataset, exp_error, exp_msg


def _gen_negative_rating_dataset():
    dataset = {'user': [2, 5, 1, 2, 3],
               'item': [4, 2, 1, 3, 4],
               'rating': [-1, 2, 3, 4, 5]}
    dataset = DataTable(pd.DataFrame(dataset))
    exp_error = error_setting.InvalidDatasetError
    exp_msg = "Training dataset of user-item-rating triples contains invalid data, dataset contains negative rating."
    return dataset, exp_error, exp_msg


def _gen_all_nan_dataset():
    dataset = {'user': [1, 2, 3],
               'item': [4, 5, 6],
               'rating': [np.nan, np.nan, np.nan]}
    dataset = DataTable(pd.DataFrame(dataset))
    exp_error = error_setting.InvalidColumnTypeError
    exp_msg = "Cannot process column \"rating\" of type NAN. The type is not supported by the module."
    return dataset, exp_error, exp_msg


@pytest.mark.parametrize('dataset,exp_error,exp_msg', [
    _gen_null_dataset(),
    _gen_invalid_column_number_dataset(),
    _gen_invalid_type_rating_dataset(),
    _gen_duplicate_rating_dataset(),
    _gen_empty_dataset(),
    _gen_negative_rating_dataset(),
    _gen_all_nan_dataset(),
])
def test_error_case(dataset, exp_error, exp_msg, entry_params):
    with pytest.raises(expected_exception=exp_error, match=exp_msg):
        TrainSVDRecommenderModule.run(training_data=dataset, **entry_params)
