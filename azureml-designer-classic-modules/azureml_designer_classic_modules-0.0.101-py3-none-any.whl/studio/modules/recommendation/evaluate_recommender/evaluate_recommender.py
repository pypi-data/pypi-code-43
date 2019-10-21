from azureml.studio.modulehost.module_reflector import BaseModule, module_entry
from azureml.studio.modulehost.attributes import ModuleMeta, ReleaseState, DataTableOutputPort, DataTableInputPort
from azureml.studio.common.error import ErrorMapping, InvalidDatasetError
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.recommendation.common.recommender_utils import build_item_recommendation_column_names
from azureml.studio.modules.recommendation.common.constants import PREDICTION_COLUMNS
from azureml.studio.modules.recommendation.evaluate_recommender.item_recommendation_evaluator import \
    ItemRecommendationEvaluator
from azureml.studio.modules.recommendation.evaluate_recommender.rating_prediction_evaluator import \
    RatingPredictionEvaluator


class EvaluateRecommenderModule(BaseModule):
    @staticmethod
    @module_entry(ModuleMeta(
        name="Evaluate Recommender",
        description="Evaluate a recommendation model",
        category="Recommendation",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="{9C4D0CB5-213E-4785-9CC8-D29CE467B9C8}",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            test_data: DataTableInputPort(
                name="Test dataset",
                friendly_name="Test dataset",
                description="Test dataset",
            ),
            scored_data: DataTableInputPort(
                name="Scored dataset",
                friendly_name="Scored dataset",
                description="Scored dataset",
            )
    ) -> (
            DataTableOutputPort(
                name="Metric",
                friendly_name="Metric",
                description="A table of evaluation metrics",
            ),
    ):
        input_values = locals()
        output_values = EvaluateRecommenderModule.evaluate_recommender(**input_values)
        return output_values

    @classmethod
    def get_recommender_evaluator(cls, scored_data: DataTable):
        if cls._is_rating_prediction_kind(scored_data):
            return RatingPredictionEvaluator()
        elif cls._is_item_recommendation_kind(scored_data):
            return ItemRecommendationEvaluator()
        else:
            ErrorMapping.throw(
                InvalidDatasetError(dataset1=cls._args.scored_data.friendly_name, reason="invalid column name(s)"))

    @classmethod
    def evaluate_recommender(cls, test_data: DataTable, scored_data: DataTable):
        evaluator = cls.get_recommender_evaluator(scored_data)
        evaluator.validate_parameters(test_data, scored_data, test_data_name=cls._args.test_data.friendly_name,
                                      scored_data_name=cls._args.scored_data.friendly_name)
        res_df = evaluator.evaluate(test_data, scored_data, test_data_name=cls._args.test_data.friendly_name,
                                    scored_data_name=cls._args.scored_data.friendly_name)
        return res_df

    @classmethod
    def _is_rating_prediction_kind(cls, scored_data: DataTable):
        return scored_data.column_names == PREDICTION_COLUMNS

    @classmethod
    def _is_item_recommendation_kind(cls, scored_data: DataTable):
        max_recommended_item_count = scored_data.number_of_columns - 1
        recommendation_column_names = build_item_recommendation_column_names(max_recommended_item_count)
        return scored_data.column_names == recommendation_column_names
