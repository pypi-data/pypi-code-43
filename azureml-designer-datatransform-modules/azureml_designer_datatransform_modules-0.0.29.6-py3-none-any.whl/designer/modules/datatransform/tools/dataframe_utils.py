import pandas as pd
from pandas.util.testing import assert_frame_equal


def compare_dataframe(table1: pd.DataFrame, table2: pd.DataFrame, with_order: bool = True):
    table1 = _clean_dataframe(table1)
    table2 = _clean_dataframe(table2)
    assert_frame_equal(table1, table2)
    return True

def _clean_dataframe(table: pd.DataFrame):
    return table.reset_index(drop=True).reindex(sorted(table.columns), axis=1)
