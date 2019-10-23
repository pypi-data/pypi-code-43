from abc import abstractmethod
import pandas as pd
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.recommendation.common.recommender_utils import get_user_column_name, get_item_column_name, \
    get_rating_column_name
from azureml.studio.common.error import ErrorMapping
from azureml.studio.common.datatable.constants import ColumnTypeName


class BaseRecommenderEvaluator:
    def __init__(self):
        pass

    def validate_parameters(self, test_data: DataTable, scored_data: DataTable):
        ErrorMapping.verify_number_of_rows_greater_than_or_equal_to(curr_row_count=test_data.number_of_rows,
                                                                    required_row_count=1,
                                                                    arg_name=test_data.name)
        ErrorMapping.verify_number_of_columns_equal_to(curr_column_count=test_data.number_of_columns,
                                                       required_column_count=3,
                                                       arg_name=test_data.name)
        ErrorMapping.verify_number_of_rows_greater_than_or_equal_to(curr_row_count=scored_data.number_of_rows,
                                                                    required_row_count=1,
                                                                    arg_name=scored_data.name)
        test_rating_column = get_rating_column_name(test_data.data_frame)
        ErrorMapping.verify_element_type(type_=test_data.get_column_type(test_rating_column),
                                         expected_type=ColumnTypeName.NUMERIC,
                                         column_name=test_rating_column)

    @abstractmethod
    def evaluate(self, test_data: DataTable, scored_data: DataTable):
        pass

    @staticmethod
    def _build_rating_lookup(df: pd.DataFrame):
        """Build lookup dictionary with user-item pair as key and rating as value.

        :param df: pd.DataFrame object with 3 columns, corresponding to (user,item,rating) triples.
        """
        user_column = get_user_column_name(df)
        item_column = get_item_column_name(df)
        rating_column = get_rating_column_name(df)
        user_item_pair = df[[user_column, item_column]].apply(tuple, axis=1)
        rating_lookup = pd.Series(df[rating_column].values, index=user_item_pair).to_dict()
        return rating_lookup
