import math
import pandas as pd
from azureml.studio.modules.recommendation.evaluate_recommender.base_recommender_evaluator import \
    BaseRecommenderEvaluator
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.recommendation.common.recommender_utils import get_rating_column_name, preprocess_triples, \
    get_user_column_name, preprocess_id_columns
from azureml.studio.modules.recommendation.common.constants import NDCG_COLUMN
from azureml.studio.common.error import ErrorMapping, InvalidDatasetError
from azureml.studio.core.logger import module_logger, TimeProfile


class ItemRecommendationEvaluator(BaseRecommenderEvaluator):
    def __init__(self):
        super().__init__()

    def validate_parameters(self, test_data: DataTable, scored_data: DataTable):
        super().validate_parameters(test_data, scored_data)
        test_rating_column = get_rating_column_name(test_data.data_frame)
        min_rating = test_data.get_column(test_rating_column).min()
        if min_rating < 0:
            ErrorMapping.throw(InvalidDatasetError(dataset1=test_data.name,
                                                   reason="dataset contains negative rating."))

    @staticmethod
    def _build_item_recommendation_result(ndcg):
        result_df = pd.DataFrame({NDCG_COLUMN: [ndcg]})
        return DataTable(result_df),

    def evaluate(self, test_data: DataTable, scored_data: DataTable):
        """Evaluate item recommendation task. The module allows duplicate recommended items for one user."""
        ndcg = 0.0

        scored_data_df = scored_data.data_frame
        scored_user_column = get_user_column_name(scored_data_df)
        module_logger.info(f"Scored data contains {scored_data.number_of_rows} samples.")
        scored_data_df = preprocess_id_columns(scored_data_df, column_subset=[scored_user_column])
        # after convert to str operation, nan values are converted to empty str
        for item_column in scored_data_df.columns[1:]:
            scored_data_df[item_column] = scored_data_df[item_column].fillna("").astype(str)
        max_recommended_item_count = scored_data.number_of_columns - 1

        test_data_df = test_data.data_frame
        module_logger.info(f"Test data contains {test_data.number_of_rows} samples.")
        test_data_df = preprocess_triples(test_data_df, dataset_name=test_data.name)
        module_logger.info(f"After preprocess, test data contains {test_data_df.shape[0]} valid samples.")
        # shift rating values for ndcg computation
        test_user_column = get_user_column_name(test_data_df)
        test_rating_column = get_rating_column_name(test_data_df)
        min_rating = test_data_df[test_rating_column].min()
        test_data_df[test_rating_column] = test_data_df[test_rating_column] - min_rating

        ground_truth_recommendation_ratings = \
            test_data_df.sort_values(by=test_rating_column, ascending=False).groupby(by=test_user_column)[
                test_rating_column].apply(lambda x: list(x)[:max_recommended_item_count]).to_dict()
        rating_lookup = self._build_rating_lookup(test_data_df)

        with TimeProfile("Evaluating item recommendation task"):
            for _, row in scored_data_df.iterrows():
                user = row[scored_user_column]
                recommended_items = row[1:]
                # filter null item represented as empty str
                recommended_items = [item for item in recommended_items if len(item) != 0]
                best_gains = ground_truth_recommendation_ratings.get(user, None)
                if best_gains is None:
                    ErrorMapping.throw(
                        InvalidDatasetError(dataset1=test_data.name,
                                            reason=f"dataset does not contain user {user}"))
                if len(best_gains) < len(recommended_items):
                    ErrorMapping.throw(
                        InvalidDatasetError(dataset1=test_data.name,
                                            reason=f"dataset does not contain enough ratings for user {user}"))
                best_gains = best_gains[:len(recommended_items)]
                ordered_gains = []
                for item in recommended_items:
                    rating = rating_lookup.get((user, item), None)
                    if rating is None:
                        ErrorMapping.throw(
                            InvalidDatasetError(dataset1=test_data.name,
                                                reason=f"dataset does not have ground truth rating "
                                                       f"for ({user},{item}) pair"))
                    ordered_gains.append(rating)
                ndcg += self.normalized_discounted_cumulative_gain(best_gains, ordered_gains)
            ndcg = ndcg / scored_data.number_of_rows
        return self._build_item_recommendation_result(ndcg)

    @staticmethod
    def normalized_discounted_cumulative_gain(best_gains, ordered_gains):
        """Return NDCG metric.

        To use this method, the length of best_gains and ordered gains is supposed to be the same.
        :param best_gains: float
        :param ordered_gains: float
        :return: float
        """
        ordered_dcg = ItemRecommendationEvaluator.discounted_cumulative_gain(
            ordered_gains, ItemRecommendationEvaluator.logarithmic_discount)
        best_dcg = ItemRecommendationEvaluator.discounted_cumulative_gain(
            best_gains, ItemRecommendationEvaluator.logarithmic_discount)
        return ordered_dcg / best_dcg if best_dcg != 0 else best_dcg

    @staticmethod
    def logarithmic_discount(x):
        """Return logarithmic discount value for NDCG metric.

        The value is set as:

        .. math::
            \frac{1.0}{log_2(x+2)}

        The index x is expected to start from 0.
        """
        return 1.0 / math.log(x + 2, 2)

    @staticmethod
    def discounted_cumulative_gain(ordered_gains, discount_func):
        return float(sum((ordered_gain * discount_func(i) for i, ordered_gain in enumerate(ordered_gains))))
