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
from azureml.studio.core.logger import module_logger, TimeProfile


class RatingPredictionEvaluator(BaseRecommenderEvaluator):
    def __init__(self):
        super().__init__()

    def validate_parameters(self, test_data: DataTable, scored_data: DataTable):
        super().validate_parameters(test_data, scored_data)
        scored_rating_column = get_rating_column_name(scored_data.data_frame)
        ErrorMapping.verify_element_type(type_=scored_data.get_column_type(scored_rating_column),
                                         expected_type=ColumnTypeName.NUMERIC,
                                         column_name=scored_rating_column)

    @staticmethod
    def _build_rating_prediction_result(mae, rmse):
        result_df = pd.DataFrame({MAE_COLUMN: [mae], RMSE_COLUMN: [rmse]})
        return DataTable(result_df),

    def evaluate(self, test_data: DataTable, scored_data: DataTable):
        mae = 0.0
        rmse = 0.0

        test_data_df = test_data.data_frame
        module_logger.info(f"Test data contains {test_data.number_of_rows} samples.")
        test_data_df = preprocess_triples(test_data_df, dataset_name=test_data.name)
        module_logger.info(f"After preprocess, test data contains {test_data_df.shape[0]} valid samples.")

        scored_data_df = scored_data.data_frame
        scored_user_column = get_user_column_name(scored_data_df)
        scored_item_column = get_item_column_name(scored_data_df)
        module_logger.info(f"Scored data contains {scored_data.number_of_rows} samples.")
        scored_rating_column = get_rating_column_name(scored_data_df)
        scored_data_df = preprocess_triples(scored_data_df, dataset_name=scored_data.name)
        module_logger.info(f"After preprocess, scored data contains {scored_data_df.shape[0]} valid samples.")

        rating_lookup = self._build_rating_lookup(test_data_df)
        with TimeProfile("Evaluating rating prediction task"):
            for _, row in scored_data_df.iterrows():
                user = row[scored_user_column]
                item = row[scored_item_column]
                pred_rating = row[scored_rating_column]
                ground_truth = rating_lookup.get((user, item), None)
                if ground_truth is None:
                    ErrorMapping.throw(
                        InvalidDatasetError(dataset1=test_data.name,
                                            reason=f"dataset does not have ground truth rating "
                                                   f"for ({user},{item}) pair"))
                mae += abs(ground_truth - pred_rating)
                rmse += (ground_truth - pred_rating) ** 2
            sample_count = scored_data_df.shape[0]
            # Sample count of processed scored data will equal to zero when all scored samples are illegal, for example:
            #       User            Item             Rating
            # 0     Bob             The Avengers     np.inf
            # 1     Dean            Titanic          np.nan
            # 2     Alice           Titanic          -np.inf
            # Also refer to the unit test test_evaluate_rating_prediction_with_zero_valid_sample()
            mae = mae / sample_count if sample_count != 0 else 0.0
            rmse = math.sqrt(rmse / sample_count) if sample_count != 0 else 0.0
        return self._build_rating_prediction_result(mae, rmse)
