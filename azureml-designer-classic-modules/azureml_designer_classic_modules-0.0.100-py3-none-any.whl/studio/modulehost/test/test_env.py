import pandas as pd
import os

from azureml.studio.modulehost.attributes import DataTableOutputPort
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.utils.fileutils import ensure_folder
from azureml.studio.modulehost.env import JesRuntimeEnv


_ENVIRON_PREFIX = 'AZUREML_DATAREFERENCE_'
_TRUE_FILE_NAMES = [
    'data.dataset',
    'data.dataset.parquet',
    'data.metadata',
    'data.schema',
    'data.visualization',
    'data_type.json'
]


def register_environmental_variable(env_variable, folder_path):
    os.environ.update({env_variable: folder_path})
    ensure_folder(folder_path)


def test_handle_output_port():
    # Construct DataTable, port_name and annotation
    dt = DataTable(pd.DataFrame({'col0': [0, 1]}))
    annotation = DataTableOutputPort(
                name="dataset",
                friendly_name="dataset",
                description="Entered data")
    port_name = "output"

    # Set environmental variable
    env_full_name = _ENVIRON_PREFIX + port_name
    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen')
    register_environmental_variable(env_full_name, folder_path)

    jes_env = JesRuntimeEnv()
    jes_env.handle_output_port(
        data=dt,
        annotation=annotation,
        param_value=port_name
    )

    for true_file_name in _TRUE_FILE_NAMES:
        print(true_file_name)
        assert os.path.isfile(os.path.join(folder_path, true_file_name))
