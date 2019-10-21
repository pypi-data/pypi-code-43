from azureml.studio.common.datatable.data_table import DataTable


class MICE:

    @classmethod
    def impute_values(
            cls, dt: DataTable, iterations: int, remove_cols_with_all_missing: bool,
            indicator_cols: bool, train: bool, col_indexes: list):
        # TODO
        pass

    @staticmethod
    def compute_mice_result(
            dt: DataTable, missing_cols: list, iterations: int,
            indicator_cols: bool, train: bool):
        # TODO
        pass

    @staticmethod
    def find_and_init_mv_columns(
            dt_in: DataTable, remove_cols_with_all_missing: bool,
            col_indexes: list, dt_out: DataTable):
        # TODO
        pass
