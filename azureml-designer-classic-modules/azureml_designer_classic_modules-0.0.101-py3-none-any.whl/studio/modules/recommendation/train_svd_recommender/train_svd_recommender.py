from azureml.studio.modulehost.module_reflector import BaseModule, module_entry
from azureml.studio.modulehost.attributes import ModuleMeta, ReleaseState, DataTableInputPort, IntParameter, \
    FloatParameter, IRecommenderOutputPort
from azureml.studio.modules.recommendation.train_svd_recommender.svd_recommender import SVDRecommender
from azureml.studio.modules.recommendation.common.recommender_utils import get_rating_column_name, preprocess_triples
from azureml.studio.common.error import ErrorMapping, InvalidDatasetError
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.constants import ColumnTypeName
from azureml.studio.internal.utils.dependencies import Dependencies


class TrainSVDRecommenderModule(BaseModule):
    @staticmethod
    @module_entry(ModuleMeta(
        name="Train SVD Recommender",
        description="Train a collaborative filtering recommendation using SVD algorithm.",
        category="Recommendation",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="{C1355F72-7199-43D3-9EE9-892232760BEC}",
        release_state=ReleaseState.Release,
        is_deterministic=True,
        conda_dependencies=Dependencies.update_from_default(
            channels=["conda-forge"],
            conda_packages=["scikit-surprise=1.0.6"]
        )
    ))
    def run(
            training_data: DataTableInputPort(
                name="Training dataset of user-item-rating triples",
                friendly_name="Training dataset of user-item-rating triples",
                description="Ratings of items by users, expressed as triple (User, Item, Rating)",
            ),
            num_factors: IntParameter(
                name="Number of factors",
                friendly_name="Number of factors",
                description="Specify the number of factors to use with recommendation",
                default_value=200,
                min_value=1,
            ),
            num_iterations: IntParameter(
                name="Number of recommendation algorithm iterations",
                friendly_name="Number of recommendation algorithm iterations",
                description="Specify the maximum number of iterations "
                            "to perform while training the recommendation model",
                default_value=30,
                min_value=1,
            ),
            # todo: Update min_value as soon as there are a common constant for min learning rate
            learning_rate: FloatParameter(
                name="Learning rate",
                friendly_name="Learning rate",
                description="Specify the size of each step in the learning process",
                default_value=0.005,
                min_value=4.94065645841247E-324,
                max_value=2.0,
            ),
    ) -> (
            IRecommenderOutputPort(
                name="Trained SVD recommendation",
                friendly_name="Trained SVD recommendation",
                description="Trained SVD recommendation",
            ),
    ):
        input_values = locals()
        output_values = TrainSVDRecommenderModule.train_svd_recommender(**input_values)
        return output_values

    @classmethod
    def _validate_parameters(cls, training_data: DataTable):
        ErrorMapping.verify_number_of_columns_equal_to(curr_column_count=training_data.number_of_columns,
                                                       required_column_count=3,
                                                       arg_name=cls._args.training_data.friendly_name)
        ErrorMapping.verify_number_of_rows_greater_than_or_equal_to(curr_row_count=training_data.number_of_rows,
                                                                    required_row_count=1,
                                                                    arg_name=cls._args.training_data.friendly_name)
        rating_column = get_rating_column_name(training_data.data_frame)
        ErrorMapping.verify_element_type(type_=training_data.get_column_type(rating_column),
                                         expected_type=ColumnTypeName.NUMERIC,
                                         column_name=rating_column)
        min_rating = training_data.get_column(rating_column).min()
        if min_rating < 0:
            ErrorMapping.throw(InvalidDatasetError(dataset1=cls._args.training_data.friendly_name,
                                                   reason="dataset contains negative rating."))

    @classmethod
    def train_svd_recommender(cls, training_data: DataTable, num_factors, num_iterations, learning_rate):
        cls._validate_parameters(training_data)
        recommender = SVDRecommender(num_factors=num_factors, num_iterations=num_iterations,
                                     learning_rate=learning_rate)
        recommender.train(preprocess_triples(training_data.data_frame))
        return recommender,
