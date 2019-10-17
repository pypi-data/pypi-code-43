import pandas as pd

from azureml.studio.modulehost.attributes import DataTableInputPort, ModuleMeta, DataTableOutputPort, ReleaseState
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.common.error import ErrorMapping, NotEqualColumnNamesError, \
    ColumnCountNotEqualError
from azureml.studio.core.logger import module_logger as logger, time_profile
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule


class AddRowsModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Add Rows",
        description="Appends a set of rows from an input dataset to the end of another dataset",
        category="Data Transformation\\Manipulation",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="b2ebdabd-217d-4915-86cc-5b05972f7270",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            table1: DataTableInputPort(
                name="Dataset1",
                friendly_name="Dataset1",
                description="Dataset rows to be added to the output dataset first",
            ),
            table2: DataTableInputPort(
                name="Dataset2",
                friendly_name="Dataset2",
                description="Dataset rows to be appended to the first dataset",
            )
    ) -> (
            DataTableOutputPort(
                name="Results dataset",
                friendly_name="Results dataset",
                description="Dataset that contains all rows of both input datasets",
            ),
    ):
        input_values = locals()

        return AddRowsModule._run_impl(**input_values),

    @classmethod
    def _run_impl(cls, table1: DataTable, table2: DataTable):
        cls._validate_columns(table1, table2)

        logger.info(f"Concat '{cls._args.table1.name}' and '{cls._args.table2.name}' into one.")
        combined_data_table = DataTable(pd.concat([table1.data_frame, table2.data_frame], ignore_index=True))

        logger.info(f"Update combined data schema.")
        _merge_table_metadata(combined_data_table.meta_data, table1.meta_data, table2.meta_data)
        return combined_data_table

    @classmethod
    def _validate_columns(cls, table1: DataTable, table2: DataTable):
        logger.info(f"Check the column number and column names of input tables.")
        if table1.number_of_columns != table2.number_of_columns:
            ErrorMapping.throw(ColumnCountNotEqualError())
        for i in range(table1.number_of_columns):
            if table1.column_names[i] != table2.column_names[i]:
                ErrorMapping.throw(NotEqualColumnNamesError(i,
                                                            f"{cls._args.table1.friendly_name}",
                                                            f"{cls._args.table2.friendly_name}"))


@time_profile
def _merge_table_metadata(
        combined_meta_data: DataFrameSchema,
        meta_data_1: DataFrameSchema,
        meta_data_2: DataFrameSchema):
    combined_meta_data.score_column_names = meta_data_2.score_column_names
    combined_meta_data.score_column_names = meta_data_1.score_column_names

    if meta_data_2.label_column_name:
        combined_meta_data.label_column_name = meta_data_2.label_column_name
    if meta_data_1.label_column_name:
        combined_meta_data.label_column_name = meta_data_1.label_column_name

    # TODO: add deep update on feature_channels if necessary
    import copy
    combined_meta_data.feature_channels.update(copy.deepcopy(meta_data_2.feature_channels))
    combined_meta_data.feature_channels.update(copy.deepcopy(meta_data_1.feature_channels))
