from .datatable.data_table import DataTable
from .error import ErrorMapping


class InputParameterChecker:

    @staticmethod
    def verify_data_table(data_table: DataTable, friendly_name):
        """
        Verify that input dataset is not null or empty
        :param data_table: The data_table specified as input to a module
        :param friendly_name: The friendly name of the table as it appears in the UI
        :return:
        """
        ErrorMapping.verify_not_null_or_empty(data_table, friendly_name)
        ErrorMapping.verify_number_of_rows_greater_than_or_equal_to(curr_row_count=data_table.number_of_rows,
                                                                    required_row_count=1,
                                                                    arg_name=friendly_name)
        ErrorMapping.verify_number_of_columns_greater_than_or_equal_to(curr_column_count=data_table.number_of_columns,
                                                                       required_column_count=1,
                                                                       arg_name=friendly_name)

    @staticmethod
    def parameter_range_check(parameter, lower_bound, upper_bound, lower_inclusive, upper_inclusive, friendly_name):
        ErrorMapping.verify_value_in_range(value=parameter, lower_bound=lower_bound, upper_bound=upper_bound,
                                           lower_inclusive=lower_inclusive, upper_inclusive=upper_inclusive,
                                           arg_name=friendly_name)
