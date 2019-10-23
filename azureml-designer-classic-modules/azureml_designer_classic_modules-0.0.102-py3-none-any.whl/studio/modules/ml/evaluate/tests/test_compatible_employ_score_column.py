import os

import pandas as pd
import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.io.data_table_io import read_data_table
from azureml.studio.modulehost.handler.sidecar_files import SideCarFileBundle
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import EvaluateModelModule
from azureml.studio.modules.ml.tests.mltest_utils import assert_data_table_equals


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def _base_library():
    return os.path.join(script_directory(), 'input', 'compatible_with_ext_prop')


@pytest.mark.parametrize(
    'scored_data_dir',
    [
        ('binary_scored_data'),
        ('regression_scored_data'),
        ('multi_scored_data'),
        ('cluster_scored_data_train'),
        ('cluster_scored_data_assign')
    ]
)
def test_compatible_with_ext_prob_data(scored_data_dir):
    scored_data = read_data_table(os.path.join(_base_library(), scored_data_dir, 'data.dataset.parquet'))
    out, = EvaluateModelModule.run(scored_data=scored_data, scored_data_to_compare=None)
    if isinstance(out, SideCarFileBundle):
        out = out.data
    ref_dt = DataTable(pd.read_parquet(os.path.join(_base_library(), scored_data_dir, 'ref_result.parquet')))

    assert_data_table_equals(data_table_now=out, data_table_ref=ref_dt)
