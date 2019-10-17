import math
import pandas as pd
from azureml.studio.modules.recommendation.evaluate_recommender.base_recommender_evaluator import \
    BaseRecommenderEvaluator
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.recommendation.common.recommender_utils import get_rating_column_name, preprocess_triples, \
    get_user_column_name, get_item_column_name
from azureml.studio.modules.recommendation.common.constants import RMSE_COLUMN, MAE_COLUMN
from azureml.studio.common.error import ErrorMapping, InvalidDatasetError
from azureml.studio.common.datatable.constants import ColumnTypeName


class RatingPredictionEvaluator(BaseRecommenderEvaluator):
    def __init__(self):
        super().__init__()

    def validate_parameters(self, test_data: DataTable, scored_data: DataTable, test_data_name=None,
                            scored_data_name=None):
        super().validate_parameters(test_data, scored_data, test_data_name, scored_data_name)
        scored_rating_column = get_rating_column_name(scored_data.data_frame)
        ErrorMapping.verify_element_type(type_=scored_data.get_column_type(scored_rating_column),
                                         expected_type=ColumnTypeName.NUMERIC,
                                         column_name=scored_rating_column)

    @staticmethod
    def _build_rating_prediction_result(mae, rmse):
        result_df = pd.DataFrame({MAE_COLUMN: [mae], RMSE_COLUMN: [rmse]})
        return DataTable(result_df),

    def evaluate(self, test_data: DataTable, scored_data: DataTable, test_data_name=None, scored_data_name=None):
        mae = 0.0
        rmse = 0.0

        test_data_df = test_data.data_frame
        test_data_df = preprocess_triples(test_data_df, dataset_name=test_data_name)

        scored_data_df = scored_data.data_frame
        scored_user_column = get_user_column_name(scored_data_df)
        scored_item_column = get_item_column_name(scored_data_df)
        scored_rating_column = get_rating_column_name(scored_data_df)
        scored_data_df = preprocess_triples(scored_data_df, dataset_name=scored_data_name)

        rating_lookup = RatingPredictionEvaluator._build_rating_lookup(test_data_df)
        for _, row in scored_data_df.iterrows():
            user = row[scored_user_column]
            item = row[scored_item_column]
            pred_rating = row[scored_rating_column]
            ground_truth = rating_lookup.get((user, item), None)
            if ground_truth is None:
                ErrorMapping.throw(
                    InvalidDatasetError(dataset1=test_data_name,
                                        reason=f"dataset does not have ground truth rating for ({user},{item}) pair"))
            mae += abs(ground_truth - pred_rating)
            rmse += (ground_truth - pred_rating) ** 2
        sample_count = scored_data.number_of_rows
        mae = mae / sample_count
        rmse = math.sqrt(rmse / sample_count)
        return RatingPredictionEvaluator._build_rating_prediction_result(mae, rmse)
