import pandas as pd
from azureml.studio.core.logger import module_logger
from azureml.studio.modulehost.attributes import DataTableInputPort, ColumnPickerParameter, \
    ModuleMeta, ReleaseState, DataTableOutputPort, SelectedColumnCategory, BooleanParameter
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.error import ErrorMapping, TooFewColumnsSelectedError, InvalidColumnCategorySelectedError
from azureml.studio.modulehost.constants import ColumnTypeName
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.datatransform.common.named_encoder import NamedOneHotEncoder


class ConvertToIndicatorValuesModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Convert to Indicator Values",
        description="Converts categorical values in columns to indicator values",
        category="Data Transformation\\Manipulation",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="6EA59C36-F283-410E-B34C-EDFABFAC39B0",
        release_state=ReleaseState.Beta,
        is_deterministic=True,
    ))
    def run(
            table: DataTableInputPort(
                name="Dataset",
                friendly_name="Dataset",
                description="Dataset with categorical columns",
            ),
            column_select: ColumnPickerParameter(
                name="Categorical columns to convert",
                friendly_name="Categorical columns to convert",
                description="Select categorical columns to convert to indicator matrices.",
                column_picker_for="Dataset",
                single_column_selection=False,
                column_selection_categories=(SelectedColumnCategory.All, ),
            ),
            overwrite: BooleanParameter(
                name="Overwrite categorical columns",
                friendly_name="Overwrite categorical columns",
                description="If True, overwrite the selected categorical columns, "
                            "otherwise append the resulting indicator matrices to the dataset",
                is_optional=True,
                default_value=False,
            ),
    ) -> (
            DataTableOutputPort(
                name="Results dataset",
                friendly_name="Results dataset",
                description="Dataset with categorical columns converted to indicator matrices.",
            ),
    ):
        input_values = locals()
        return ConvertToIndicatorValuesModule._run_impl(**input_values)

    @classmethod
    def _run_impl(
            cls,
            table: DataTable,
            column_select: DataTableColumnSelection,
            overwrite: bool = False):
        """Generate indicator values of selected categorical columns with correct meta data

        :param table: DataTable
        :param column_select: ColumnSelection
        :param overwrite: bool
        :return: DataTable
        """
        ErrorMapping.verify_not_null_or_empty(x=table, name=cls._args.table.friendly_name)
        ErrorMapping.verify_not_null_or_empty(x=column_select, name=cls._args.column_select.friendly_name)
        ErrorMapping.verify_number_of_columns_greater_than_or_equal_to(
            curr_column_count=table.number_of_columns, required_column_count=1, arg_name=cls._args.table.friendly_name)
        selected_col_indices = column_select.select_column_indexes(table)
        if len(selected_col_indices) == 0:
            ErrorMapping.throw(TooFewColumnsSelectedError(
                arg_name=cls._args.table.friendly_name, required_columns_count=1))

        module_logger.info('Get target categorical column indices')
        # Need to get target categorical column indices in case we have to overwrite them
        target_category_col_indices = []
        target_category_col_names = []
        for index in sorted(selected_col_indices):
            if table.get_column_type(index) == ColumnTypeName.CATEGORICAL:
                target_category_col_indices.append(index)
                target_category_col_names.append(table.get_column_name(index))
            else:
                # Will throw InvalidColumnCategorySelectedError if any selected column is not categorical
                ErrorMapping.throw(InvalidColumnCategorySelectedError(col_name=table.get_column_name(index)))

        for cur_col_name in target_category_col_names:
            module_logger.info(f'For categorical column {cur_col_name}, generate indicator dataframe')
            cur_col_series = table.data_frame[cur_col_name]
            cur_col_is_feature = table.meta_data.column_attributes[cur_col_name].is_feature
            new_cols_df = cls.generate_indicator_df(cur_col_series, cur_col_name)
            new_cols_name = new_cols_df.columns.values.tolist()
            # Get current col num of table before adding new indicator values of current categorical col
            cur_table_col_num = table.number_of_columns
            for col_name in new_cols_name:
                table.add_column(col_name, new_cols_df[col_name])
            # Indicator values will be created as feature field by default. However, if current column is
            # of label field, they should not be either label or feature field based on V1,
            if not cur_col_is_feature:
                col_indices = [cur_table_col_num + i for i in range(new_cols_df.shape[1])]
                table.clear_features(col_indices)

        if overwrite:
            module_logger.info('Overwrite target categorical columns')
            permuted_indices = list(set(range(table.number_of_columns)) - set(target_category_col_indices))
            table = table.get_slice_by_column_indexes(permuted_indices, if_clone=False)
        return table,

    @classmethod
    def generate_indicator_df(cls, series: pd.Series, cur_col_name: str):
        """Use NamedOneHotEncoder to generate indicator values

        :param series: pd.Series
        :param cur_col_name: str
        :return: pd.DataFrame
        """
        named_encoder = NamedOneHotEncoder(cur_col_name)
        indicator_matrix = named_encoder.fit_transform(series)
        enc = named_encoder.one_hot_encoder
        indicator_df_column_names = [f"{cur_col_name}-{category_name}" for category_name in enc.categories_[0]]
        indicator_df = pd.DataFrame(indicator_matrix.todense(), columns=indicator_df_column_names)
        return indicator_df
