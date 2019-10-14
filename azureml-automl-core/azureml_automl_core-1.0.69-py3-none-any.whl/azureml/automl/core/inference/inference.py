# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pkg_resources
import os
from typing import Any, Tuple, cast
from azureml.automl.core.package_utilities import _all_dependencies


PACKAGE_NAME = 'azureml.automl.core'
NumpyParameterType = 'NumpyParameterType'
PandasParameterType = 'PandasParameterType'
AutoMLCondaPackagesList = ['numpy>=1.16.0,<=1.16.2', 'pandas',
                           'scikit-learn', 'py-xgboost<=0.80', 'fbprophet==0.5']
AutoMLPipPackagesList = ['azureml-train-automl', 'inference-schema']
AMLArtifactIDHeader = 'aml://artifact/'
MaxLengthModelID = 29


class AutoMLInferenceArtifactIDs:
    CondaEnvDataLocation = 'conda_env_data_location'
    ScoringDataLocation = 'scoring_data_location'
    ModelName = 'model_name'
    ModelDataLocation = 'model_data_location'
    PipelineGraphVersion = 'pipeline_graph_version'


def _extract_parent_run_id_and_child_iter_number(run_id: str) -> Any:
    """
    Extract and return the parent run id and child iteration number.
    """
    parent_run_length = run_id.rfind('_')
    parent_run_id = run_id[0:parent_run_length]
    child_run_number_str = run_id[parent_run_length + 1: len(run_id)]
    try:
        # Attempt to convert child iteration number string to integer
        int(child_run_number_str)
        return parent_run_id, child_run_number_str
    except ValueError:
        return None, None


def _get_model_name(run_id: str) -> Any:
    """
    Return a model name from an AzureML run-id.

    Examples:- Input = AutoML_2cab0bf2-b6ae-4f57-b8fe-5feb13c60a5f_24
               Output = AutoML2cab0bf2b24
               Input = AutoML_2cab0bf2-b6ae-4f57-b8fe-5feb13c60a5f
               Output = AutoML2cab0bf2b
               Input = 2cab0bf2-b6ae-4f57-b8fe-5feb13c60a5f_24
               Output = 2cab0bf2b6ae4f524
    """
    run_guid, child_run_number = _extract_parent_run_id_and_child_iter_number(run_id)
    if run_guid is None:
        return run_id.replace('_', '').replace('-', '')[:MaxLengthModelID]
    else:
        return (run_guid.replace('_', '').replace('-', '')[:15] + child_run_number)[:MaxLengthModelID]


def _get_scoring_file(if_pandas_type: bool, input_sample_str: str,
                      automl_run_id: str, is_forecasting: bool = False) -> Tuple[str, str]:
    """
    Return scoring file to be used at the inference time.

    If there are any changes to the scoring file, the version of the scoring file should
    be updated in the vendor.

    :return: Scoring python file as a string
    """
    if not is_forecasting:
        scoring_file_path = pkg_resources.resource_filename(
            PACKAGE_NAME, os.path.join('inference', 'score.txt'))
    else:
        scoring_file_path = pkg_resources.resource_filename(
            PACKAGE_NAME, os.path.join('inference', 'score_forecasting.txt'))

    inference_data_type = NumpyParameterType
    if if_pandas_type:
        inference_data_type = PandasParameterType

    content = None
    model_id = _get_model_name(automl_run_id)
    with open(scoring_file_path, 'r') as scoring_file_ptr:
        content = scoring_file_ptr.read()
        content = content.replace('<<ParameterType>>', inference_data_type)
        content = content.replace('<<input_sample>>', input_sample_str)
        content = content.replace('<<modelid>>', model_id)

    return content, model_id


def _create_conda_env_file() -> Any:
    """
    Return conda/pip dependencies for the current AutoML run.

    If there are any changes to the conda environment file, the version of the conda environment
    file should be updated in the vendor.

    :return: Conda dependencies as string
    """
    from azureml.core.conda_dependencies import CondaDependencies
    sdk_dependencies = _all_dependencies()
    pip_package_list_with_version = []
    for pip_package in AutoMLPipPackagesList:
        if 'azureml' in pip_package:
            if pip_package in sdk_dependencies:
                pip_package_list_with_version.append(pip_package + "==" + sdk_dependencies[pip_package])
        else:
            pip_package_list_with_version.append(pip_package)

    myenv = CondaDependencies.create(conda_packages=AutoMLCondaPackagesList,
                                     pip_packages=pip_package_list_with_version,
                                     pin_sdk_version=False)

    return myenv.serialize_to_string()
