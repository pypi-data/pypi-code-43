import pytest
import pandas as pd
import numpy as np
import os
import azureml.studio.common.error as error_setting
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.recommendation.evaluate_recommender.evaluate_recommender import EvaluateRecommenderModule
from azureml.studio.modules.recommendation.common.recommender_utils import build_item_recommendation_column_names
from azureml.studio.modules.recommendation.common.constants import PREDICTION_COLUMNS


def _gen_null_test_data():
    test_data = None
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.NullOrEmptyError
    exp_msg = "Input \"Test dataset\" is null or empty."
    return test_data, scored_data, exp_error, exp_msg


def _gen_null_scored_data():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = None
    exp_error = error_setting.NullOrEmptyError
    exp_msg = "Input \"Scored dataset\" is null or empty."
    return test_data, scored_data, exp_error, exp_msg


def _gen_empty_test_data():
    test_data = DataTable(pd.DataFrame({}, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.TooFewRowsInDatasetError
    exp_msg = r'Number of rows in input dataset "Test dataset" is 0, less than allowed minimum of 1 row\(s\).'
    return test_data, scored_data, exp_error, exp_msg


def _gen_empty_scored_data():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = DataTable(pd.DataFrame({}, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.TooFewRowsInDatasetError
    exp_msg = r"Number of rows in input dataset \"Scored dataset\" is 0, less than allowed minimum of 1 row\(s\)."
    return test_data, scored_data, exp_error, exp_msg


def _gen_invalid_column_number_test_data():
    test_data = [['sam', 'the avengers', 4, 'a'],
                 ['dean', 'titanic', 5, 'b'],
                 ['sam', 'supernatural', 6, 'c']]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating', 'extra_col']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.UnexpectedNumberOfColumnsError
    error_msg = r"In input dataset \"Test dataset\", expected \"3\" column\(s\) but found \"4\" column\(s\) instead."
    return test_data, scored_data, exp_error, error_msg


def _gen_invalid_rating_column_type_test_data():
    test_data = [['sam', 'the avengers', 'a'],
                 ['dean', 'titanic', 'b'],
                 ['sam', 'supernatural', 'c']]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.InvalidColumnTypeError
    error_msg = "Cannot process column \"rating\" of type String. The type is not supported by the module."
    return test_data, scored_data, exp_error, error_msg


def _gen_duplicate_rating_test_data():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6],
                 ['sam', 'supernatural', 7]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.MoreThanOneRatingError
    error_msg = "More than one rating for user sam and item supernatural in Test dataset."
    return test_data, scored_data, exp_error, error_msg


def _gen_invalid_column_name_scored_data():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers'],
                   ['dean', 'titanic'],
                   ['sam', 'supernatural']]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS[:2]))
    exp_error = error_setting.InvalidDatasetError
    error_msg = r"Scored dataset contains invalid data, invalid column name\(s\)."
    return test_data, scored_data, exp_error, error_msg


def _gen_invalid_rating_column_type_scored_data():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'a'],
                   ['dean', 'titanic', 'c']]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.InvalidColumnTypeError
    error_msg = "Cannot process column \"Rating\" of type String. The type is not supported by the module."
    return test_data, scored_data, exp_error, error_msg


def _gen_duplicate_rating_scored_data():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3],
                   ['dean', 'titanic', 2]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.MoreThanOneRatingError
    error_msg = "More than one rating for user dean and item titanic in Scored dataset."
    return test_data, scored_data, exp_error, error_msg


def _gen_nan_ground_truth_for_rating_prediction():
    test_data = [['sam', 'the avengers', np.nan],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, " \
                r"dataset does not have ground truth rating for \(sam,the avengers\) pair."
    return test_data, scored_data, exp_error, error_msg


def _gen_inf_ground_truth_for_rating_prediction():
    test_data = [['sam', 'the avengers', -np.inf],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 1],
                   ['dean', 'titanic', 2],
                   ['sam', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, " \
                r"dataset does not have ground truth rating for \(sam,the avengers\) pair."
    return test_data, scored_data, exp_error, error_msg


def _gen_nan_ground_truth_for_item_recommendation():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6],
                 ['dean', 'the avengers', 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'supernatural'],
                   ['dean', 'supernatural', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, " \
                r"dataset does not have ground truth rating for \(dean,supernatural\) pair."
    return test_data, scored_data, exp_error, error_msg


def _gen_inf_ground_truth_for_item_recommendation():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6],
                 ['dean', 'the avengers', 4],
                 ['dean', 'supernatural', np.inf]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'supernatural'],
                   ['dean', 'supernatural', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, " \
                r"dataset does not have ground truth rating for \(dean,supernatural\) pair."
    return test_data, scored_data, exp_error, error_msg


def _gen_too_few_ratings_for_item_recommendation():
    test_data = [['sam', 'the avengers', 4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'supernatural', 'the avengers'],
                   ['dean', 'supernatural', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, dataset does not contain enough ratings for user dean."
    return test_data, scored_data, exp_error, error_msg


def _gen_missing_user_for_item_recommendation():
    test_data = [['sam', 'the avengers', 5],
                 ['sam', 'supernatural', 6]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'supernatural'],
                   ['dean', 'supernatural', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, dataset does not contain user dean."
    return test_data, scored_data, exp_error, error_msg


def _gen_negative_rating_test_data_for_item_recommendation():
    test_data = [['sam', 'the avengers', -4],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6],
                 ['dean', 'the avengers', 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'supernatural'],
                   ['dean', 'titanic', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    exp_error = error_setting.InvalidDatasetError
    error_msg = "Test dataset contains invalid data, dataset contains negative rating."
    return test_data, scored_data, exp_error, error_msg


@pytest.mark.parametrize('test_data,scored_data,exp_error,exp_msg', [
    _gen_null_test_data(),
    _gen_null_scored_data(),
    _gen_empty_test_data(),
    _gen_empty_scored_data(),
    _gen_invalid_column_number_test_data(),
    _gen_invalid_rating_column_type_test_data(),
    _gen_duplicate_rating_test_data(),
    _gen_invalid_column_name_scored_data(),
    _gen_invalid_rating_column_type_scored_data(),
    _gen_duplicate_rating_scored_data(),
    _gen_nan_ground_truth_for_rating_prediction(),
    _gen_inf_ground_truth_for_rating_prediction(),
    _gen_nan_ground_truth_for_item_recommendation(),
    _gen_inf_ground_truth_for_item_recommendation(),
    _gen_too_few_ratings_for_item_recommendation(),
    _gen_missing_user_for_item_recommendation(),
    _gen_negative_rating_test_data_for_item_recommendation(),
])
def test_error_case(test_data, scored_data, exp_error, exp_msg):
    with pytest.raises(expected_exception=exp_error, match=exp_msg):
        EvaluateRecommenderModule.run(test_data=test_data, scored_data=scored_data)


@pytest.fixture
def input_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'input')
    return input_dir


@pytest.fixture
def ground_truth_data(input_dir):
    ground_truth_path = os.path.join(input_dir, 'ground_truth_movie_dataset.csv')
    ground_truth_data = DataTable(pd.read_csv(ground_truth_path))
    return ground_truth_data


def test_evaluate_rating_prediction_with_imported_data(ground_truth_data, input_dir):
    scored_data_path = os.path.join(input_dir, 'scored_movie_dataset_for_rating_prediction.csv')
    scored_data = DataTable(pd.read_csv(scored_data_path))
    res = EvaluateRecommenderModule.run(test_data=ground_truth_data, scored_data=scored_data)[0]
    assert res.number_of_rows == 1
    assert res.number_of_columns == 2
    assert res.column_names == ['MAE', 'RMSE']


def test_evaluate_items_recommendation_with_imported_data(ground_truth_data, input_dir):
    scored_data_path = os.path.join(input_dir, 'scored_movie_dataset_for_rated_items_recommendation.csv')
    scored_data = DataTable(pd.read_csv(scored_data_path))
    res = EvaluateRecommenderModule.run(test_data=ground_truth_data, scored_data=scored_data)[0]
    assert res.number_of_rows == 1
    assert res.number_of_columns == 1
    assert res.column_names == ['NDCG']
    assert 0 < res.data_frame.iloc[0, 0] < 1.0


def test_evaluate_items_recommendation_with_zero_rating():
    test_data = [['sam', 'the avengers', 0],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6],
                 ['dean', 'the avengers', 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'supernatural'],
                   ['dean', 'titanic', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    res = EvaluateRecommenderModule.run(test_data=test_data, scored_data=scored_data)[0]
    ndcg = res.data_frame.iloc[0, 0]
    assert 0 < ndcg < 1.0


def test_evaluate_rating_prediction_with_nan_scored_data():
    test_data = [['sam', 'the avengers', 2],
                 ['dean', 'titanic', 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', np.nan],
                   ['dean', 'titanic', 4]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    res = EvaluateRecommenderModule.run(test_data=test_data, scored_data=scored_data)[0]
    assert res.data_frame.iloc[0, 0] == 0 and res.data_frame.iloc[0, 1] == 0


def test_evaluate_rating_prediction_with_inf_scored_data():
    test_data = [['sam', 'the avengers', 2],
                 ['dean', 'titanic', 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', np.inf],
                   ['dean', 'the avengers', -np.inf],
                   ['dean', 'titanic', 4]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    res = EvaluateRecommenderModule.run(test_data=test_data, scored_data=scored_data)[0]
    assert res.data_frame.iloc[0, 0] == 0 and res.data_frame.iloc[0, 1] == 0


def test_duplicate_item_recommendation_scored_data():
    test_data = [['sam', 'the avengers', 0],
                 ['dean', 'titanic', 5],
                 ['sam', 'supernatural', 6],
                 ['dean', 'the avengers', 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['sam', 'the avengers', 'the avengers'],
                   ['dean', 'titanic', 'the avengers']]
    scored_data = DataTable(
        pd.DataFrame(data=scored_data, columns=build_item_recommendation_column_names(max_recommended_item_count=2)))
    EvaluateRecommenderModule.run(test_data=test_data, scored_data=scored_data)


def test_multi_type_id_data():
    test_data = [[1, False, 0],
                 ['dean', True, 5],
                 [5.5, 'supernatural', 6],
                 ['dean', False, 4]]
    test_data = DataTable(pd.DataFrame(data=test_data, columns=['user', 'item', 'rating']))
    scored_data = [['1', 'False', 2],
                   ['5.5', 'supernatural', 3]]
    scored_data = DataTable(pd.DataFrame(data=scored_data, columns=PREDICTION_COLUMNS))
    EvaluateRecommenderModule.run(test_data=test_data, scored_data=scored_data)
