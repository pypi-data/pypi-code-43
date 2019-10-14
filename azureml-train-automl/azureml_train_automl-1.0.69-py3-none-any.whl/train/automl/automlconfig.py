# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Configuration for submitting a local Automated Machine Learning experiment.

Classes include methods for defining training features and labels, iteration count and max time, optimization
metrics, compute targets, and algorithms to blacklist.
"""
from typing import Any, Callable, Dict, List, Optional, Union
import inspect
import logging
import math
import os
import pickle as pkl
import shutil
import sys

from . import constants
from azureml.automl.core import dataprep_utilities
from azureml.automl.core import dataset_utilities
from azureml.automl.core.featurization import FeaturizationConfig
from .exceptions import ConfigException
from .constants import FeaturizationConfigMode
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._base_sdk_common.workspace.models import ProvisioningState
from ._remote_console_interface import RemoteConsoleInterface
from ._azureautomlclient import AzureAutoMLClient
from ._azureautomlsettings import AzureAutoMLSettings
from ._logging import get_logger
from ._environment_utilities import modify_run_configuration
from azureml.core import ScriptRunConfig, Run
from azureml.core._experiment_method import experiment_method
from azureml.core.workspace import Workspace
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration


def _automl_static_submit(automl_config_object: 'AutoMLConfig',
                          workspace: Workspace,
                          experiment_name: str,
                          **kwargs: Any) -> Run:
    """
    Start AutoML execution with the given config on the given workspace.

    :param automl_config_object:
    :param workspace:
    :param experiment_name:
    :param kwargs:
    :return:
    """
    experiment = Experiment(workspace, experiment_name)
    show_output = kwargs.get('show_output', False)

    in_process = False
    if automl_config_object._run_configuration is None:
        in_process = True

    automl_config_object._validate_config_settings(workspace)
    automl_config_object._get_remove_fit_params()

    settings = automl_config_object.user_settings
    fit_params = automl_config_object.fit_params

    run_config = fit_params['run_configuration']

    if in_process is True:
        try:
            automl_run = _default_execution(experiment, settings, fit_params, show_output)
        except ImportError:
            run_config = RunConfiguration()
            automl_run = _local_managed(experiment, run_config, settings, fit_params)
            from azureml.train.automl.run import AutoMLRun
            if show_output and isinstance(automl_run, AutoMLRun):
                RemoteConsoleInterface._show_output(automl_run,
                                                    sys.stdout,
                                                    None,
                                                    settings['primary_metric'])
    elif run_config.target == 'local':
        print("Running on local conda or docker.")
        automl_run = _local_managed(experiment, run_config, settings, fit_params)
    else:
        print("Running on remote or ADB.")
        automl_run = _default_execution(experiment, settings, fit_params, show_output)

    tracking_path = automl_config_object.user_settings.get('path') or '.'
    automl_run.add_properties(global_tracking_info_registry.gather_all(tracking_path))

    return automl_run


def _default_execution(experiment: Experiment,
                       automl_settings: Dict[str, Any],
                       fit_params: Dict[str, Any],
                       show_output: Optional[bool] = False) -> Run:
    from azureml.train.automl.constants import AUTOML_SETTINGS_PATH, AUTOML_FIT_PARAMS_PATH
    # from azureml.train.automl.placeholder.submit import _automl_static_submit
    from azureml.train.automl._azureautomlclient import AzureAutoMLClient
    fit_params['show_output'] = show_output

    settings_obj = AzureAutoMLSettings(experiment, **automl_settings)
    automl_estimator = AzureAutoMLClient(experiment, settings_obj)

    return automl_estimator.fit(**fit_params)


def _local_managed(experiment: Experiment,
                   run_config: RunConfiguration,
                   settings: Dict[str, Any],
                   fit_params: Dict[str, Any]) -> Run:
    package_dir = os.path.dirname(os.path.abspath(__file__))
    local_path = settings.get('path')
    if local_path is None:
        local_path = '.'

    script_path = os.path.join(package_dir, constants.LOCAL_SCRIPT_NAME)
    shutil.copy(script_path, os.path.join(local_path, constants.LOCAL_SCRIPT_NAME))

    run_config.environment.python.user_managed_dependencies = False
    run_config = modify_run_configuration(AzureAutoMLSettings(**settings), run_config, get_logger())

    # if we don't want to do experiment.submit, we can do below instead
    """
    project = workspace._initialize_folder(experiment_name, directory=settings['path'])
    run_config = RunConfiguration._get_run_config_object(path=settings['path'], run_config=run_config)

    run_config.script = constants.LOCAL_SCRIPT_NAME
    script_run = _commands.start_run(project, run_config)
    """

    with open(os.path.join(local_path, constants.AUTOML_SETTINGS_PATH), 'wb+') as file:
        pkl.dump(settings, file)
    with open(os.path.join(local_path, constants.AUTOML_FIT_PARAMS_PATH), 'wb+') as file:
        pkl.dump(fit_params, file)

    src = ScriptRunConfig(source_directory=local_path, script=constants.LOCAL_SCRIPT_NAME, run_config=run_config)

    script_run = experiment.submit(src)

    parent_run_id = None
    while parent_run_id is None:
        parent_run_id = script_run.get_properties().get("automl_id", None)
        if script_run.get_status() in ['Completed', 'Failed', 'Canceled']:
            parent_run_id = script_run.get_properties().get("automl_id", None)
            break

    if parent_run_id is None:
        return script_run

    from .run import AutoMLRun
    automl_run = AutoMLRun(experiment, parent_run_id)

    return automl_run


class AutoMLConfig(object):
    """
    Configuration for submitting an Automated Machine Learning experiment in Azure Machine Learning service.

    This configuration object contains and persists the parameters for configuring
    the experiment run parameters, as well as the training data to be used at run time. For guidance on selecting
    your settings, you may refer to
    https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-auto-train.
    The following code shows a basic example of creating an AutoMLConfig object, and submitting an
    experiment with the defined configuration:

    .. code-block:: python

        from azureml.core.experiment import Experiment
        from azureml.core.workspace import Workspace
        from azureml.train.automl import AutoMLConfig

        automated_ml_config = AutoMLConfig(task = 'regression',
                                 X = your_training_features,
                                 y = your_training_labels,
                                 iterations=30,
                                 iteration_timeout_minutes=5,
                                 primary_metric="spearman_correlation")

        ws = Workspace.from_config()
        experiment = Experiment(ws, "your-experiment-name")
        run = experiment.submit(automated_ml_config, show_output=True)


    :param task: 'classification', 'regression', or 'forecasting' depending on what kind of ML problem to solve.
    :type task: str or azureml.train.automl.constants.Tasks
    :param path: Full path to the Azure Machine Learning project folder.
    :type path: str
    :param iterations:
        Total number of different algorithm and parameter combinations
        to test during an Automated Machine Learning experiment.
    :type iterations: int
    :param data_script: File path to the user authored script containing get_data() function.
    :type data_script: str
    :param primary_metric:
        The metric that Automated Machine Learning will optimize for model selection.
        Automated Machine Learning collects more metrics than it can optimize.
        You may use azureml.train.automl.utilities.get_primary_metrics(task) to get a list of
        valid metrics for your given task. You may reference
        https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-auto-train
        for details on how these metrics are calculated.
    :type primary_metric: str or azureml.train.automl.constants.Metric
    :param compute_target: The Azure Machine Learning compute target to run the
        Automated Machine Learning experiment on.
        See https://docs.microsoft.com/azure/machine-learning/service/how-to-auto-train-remote for more
        information on compute targets.
    :type compute_target: azureml.core.compute.AbstractComputeTarget
    :param spark_context: Spark context, only applicable when used inside Azure Databricks/Spark environment.
    :type spark_context: SparkContext
    :param X: The training features to use when fitting pipelines during an experiment.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param y: Training labels to use when fitting pipelines during an experiment.
        This is the value your model will predict.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param sample_weight:
        The weight to give to each training sample when running fitting pipelines,
        each row should correspond to a row in X and y data.
    :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        or azureml.data.TabularDataset
    :param X_valid: validation features to use when fitting pipelines during an experiment.
    :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param y_valid: validation labels to use when fitting pipelines during an experiment.
    :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param sample_weight_valid:
        The weight to give to each validation sample when running scoring pipelines,
        each row should correspond to a row in X and y data.
    :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        or azureml.data.TabularDataset
    :param cv_splits_indices:
        Indices where to split training data for cross validation.
        Each row is a separate cross fold and within each crossfold, provide 2 arrays, t
        he first with the indices for samples to use for training data and the second with the indices to
        use for validation data. i.e [[t1, v1], [t2, v2], ...] where t1 is the training indices for the first cross
        fold and v1 is the validation indices for the first cross fold.
    :type cv_splits_indices: numpy.ndarray
    :param validation_size:
        What percent of the data to hold out for validation when user validation data
        is not specified.
    :type validation_size: float
    :param n_cross_validations: How many cross validations to perform when user validation data is not specified.
    :type n_cross_validations: int
    :param y_min:
        Minimum value of y for a regression experiment. The combination of y_min and y_max are used to normalize
        test set metrics based on the file data range.
    :type y_min: float
    :param y_max:
        Maximum value of y for a regression experiment. The combination of y_min and y_max are used to normalize
        test set metrics based on the file data range.
    :type y_max: float
    :param num_classes: Number of classes in the label data for a classification experiment.
    :type num_classes: int
    :param featurization:
        'auto' / 'off' / FeaturizationConfig
        Indicator for whether featurization step should be done automatically or not,
        or whether customized featurization should be used.
        Note: If the input data is sparse, featurization cannot be turned on.

        Column type is automatically detected. Based on the detected column type
        preprocessing/featurization is done as follows:

        Categorical: Target encoding, one hot encoding, drop high cardinality categories, impute missing values.
        Numeric: Impute missing values, cluster distance, weight of evidence.
        DateTime: Several features such as day, seconds, minutes, hours etc.
        Text: Bag of words, pre-trained Word embedding, text target encoding.

        More details can be found here:
        https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-create-portal-experiments#advanced-preprocessing-options

        To customize featurization step, provide FeaturizationConfig object.
        Customized featurization currently supports blocking a set of transformers, updating column purpose,
        editing transformer parameters, and dropping columns.

        Note: Timeseries features are handled separately when the task type is set to forecasting independent
        of this parameter.
    :type featurization: str or FeaturizationConfig
    :param lag_length: How many rows of historical data to include when preprocessing time series data.
    :type lag_length: int
    :param max_cores_per_iteration: Maximum number of threads to use for a given training iteration.
        This should be less than or equal to the maximum number of cores on the compute target.
    :type max_cores_per_iteration: int
    :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel on an amlcompute
            cluster, on a DSVM, or on Databricks. This should be less than or equal to the number
            of cores on the amlcompute/DSVM or worker nodes on Databricks. If you run multiple
            experiments in parallel on a single amlcompute cluster or DSVM, the sum of the
            max_concurrent_iterations values should be less than or equal to the maximum number of nodes.
            It does not apply to local runs. Formerly concurrent_iterations.
    :type max_concurrent_iterations: int
    :param iteration_timeout_minutes:
        Maximum time in minutes that each iteration can run for before it terminates.
    :type iteration_timeout_minutes: int
    :param mem_in_mb: Maximum memory usage that each iteration can run for before it terminates.
    :type mem_in_mb: int
    :param enforce_time_on_windows:
        Flag to enforce time limit on model training at each iteration under windows.
        If running from a python script file (.py) please refer to the documentation for allowing resource limits
        on windows.
    :type enforce_time_on_windows: bool
    :param experiment_timeout_minutes:
        Maximum amount of time in minutes that all iterations combined can take before the
        experiment terminates.
    :type experiment_timeout_minutes: int
    :param experiment_exit_score:
        Target score for experiment. Experiment will terminate after this score is reached.
    :type experiment_exit_score: float
    :param enable_early_stopping:
        Flag to enble early termination if the score is not improving in the short term.
    :type enable_early_stopping: bool
    :param blacklist_models: List of algorithms to ignore for an experiment.
    :type blacklist_models: list(str) or list(azureml.train.automl.constants.SupportedModels.Classification) for
        classification task, or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task, or
        list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task.
    :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label.
    :type exclude_nan_labels: bool
    :param verbosity: Verbosity level for log file.
    :type verbosity: int
    :param enable_tf:  Flag to enable/disable Tensorflow algorithms
    :type enable_tf: bool
    :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
    :type enable_cache: bool
    :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
        COST_FILTER stands for cost prediction per iteration.
    :type cost_mode: int or automl.client.core.common.constants.PipelineCost
    :param whitelist_models: List of model names to search for an experiment.
    :type whitelist_models: list(str) or list(azureml.train.automl.constants.SupportedModels.Classification) for
        classification task, or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task, or
        list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task.
    :param enable_onnx_compatible_models: Flag to enable/disable enforcing the onnx compatible models.
    :type enable_onnx_compatible_models: bool
    :param time_column_name: The name of your time column.
    :type time_column_name: str
    :param max_horizon: The number of periods out you would like to predict past your training data.
        Periods are inferred from your data.
    :type max_horizon: int
    :param grain_column_names: The names of columns used to group your timeseries.
        It can be used to create multiple series.
    :type grain_column_names: List[str]
    :param drop_column_names: The names of columns to drop.
    :type drop_column_names: List[str]
    :param target_lags: The number of past periods to lag from the target column.
    :type target_lags: int
    :param target_rolling_window_size: The number of past periods used to create a
        rolling window average of the target column.
    :type target_rolling_window_size: int
    :param country_or_region: The country/region used to generate holiday features.
        These should be ISO 3166 two-letter country/region codes (i.e. 'US', 'GB').
    :type country_or_region: str
    :param enable_voting_ensemble: Flag to enable/disable VotingEnsemble iteration.
    :type enable_voting_ensemble: bool
    :param enable_stack_ensemble: Flag to enable/disable StackEnsemble iteration.
    :type enable_stack_ensemble: bool
    :param debug_log: Log file to write debug information to.
    :type debug_log: str
    :param training_data: The training data to be used within the experiment.
        It should contain both training features and label column (optionally a sample weights column).
    :type training_data: pandas.DataFrame or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param validation_data: The validation data to be used within the experiment.
        It should contain both training features and label column (optionally a sample weights column).
    :type validation_data: pandas.DataFrame or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param label_column_name: The name of the label column.
    :type label_column_name: str
    :param weight_column_name: The name of the sample weight column.
    :type weight_column_name: str
    """

    @experiment_method(submit_function=_automl_static_submit)
    def __init__(self,
                 task: str,
                 path: Optional[str] = None,
                 iterations: Optional[int] = None,
                 data_script: Optional[str] = None,
                 primary_metric: Optional[str] = None,
                 compute_target: Optional[Any] = None,
                 spark_context: Optional[Any] = None,
                 X: Optional[Any] = None,
                 y: Optional[Any] = None,
                 sample_weight: Optional[Any] = None,
                 X_valid: Optional[Any] = None,
                 y_valid: Optional[Any] = None,
                 sample_weight_valid: Optional[Any] = None,
                 cv_splits_indices: Optional[Any] = None,
                 validation_size: Optional[float] = None,
                 n_cross_validations: Optional[int] = None,
                 y_min: Optional[float] = None,
                 y_max: Optional[float] = None,
                 num_classes: Optional[int] = None,
                 featurization: Union[str, FeaturizationConfig] = FeaturizationConfigMode.Off,
                 lag_length: int = 0,
                 max_cores_per_iteration: int = 1,
                 max_concurrent_iterations: int = 1,
                 iteration_timeout_minutes: Optional[int] = None,
                 mem_in_mb: Optional[int] = None,
                 enforce_time_on_windows: bool = os.name == 'nt',
                 experiment_timeout_minutes: Optional[int] = None,
                 experiment_exit_score: Optional[float] = None,
                 enable_early_stopping: bool = False,
                 blacklist_models: Optional[List[str]] = None,
                 exclude_nan_labels: bool = True,
                 verbosity: int = logging.INFO,
                 enable_tf: bool = False,
                 enable_cache: bool = True,
                 cost_mode: int = constants.PipelineCost.COST_NONE,
                 whitelist_models: Optional[List[str]] = None,
                 enable_onnx_compatible_models: bool = False,
                 enable_voting_ensemble: bool = True,
                 enable_stack_ensemble: bool = True,
                 debug_log: str = 'automl.log',
                 training_data: Optional[Any] = None,
                 validation_data: Optional[Any] = None,
                 label_column_name: Optional[str] = None,
                 weight_column_name: Optional[str] = None,
                 **kwargs: Any) -> None:
        """
        Create an AutoMLConfig.

        :param task: 'classification', 'regression', or 'forecasting' depending on what kind of ML problem.
        :type task: str or azureml.train.automl.constants.Tasks
        :param path: Full path to the AzureML project folder.
        :type path: str
        :param iterations:
            Total number of different algorithm and parameter combinations
            to test during an AutoML experiment.
        :type iterations: int
        :param data_script: File path to the user authored script containing get_data() function.
        :type data_script: str
        :param primary_metric:
            The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            You may use azureml.train.automl.utilities.get_primary_metrics(task) to get a list of
            valid metrics for your given task. You may reference
            https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-configure-auto-train
            for details on how these metrics are calculated.
        :type primary_metric: str or azureml.train.automl.constants.Metric
        :param compute_target: The AzureML compute to run the AutoML experiment on.
        :type compute_target: azureml.core.compute.AbstractComputeTarget
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
        :param X: The training features to use when fitting pipelines during AutoML experiment.
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param y: Training labels to use when fitting pipelines during AutoML experiment.
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param sample_weight:
            The weight to give to each training sample when running fitting pipelines,
            each row should correspond to a row in X and y data.
        :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
            or azureml.data.TabularDataset
        :param X_valid: validation features to use when fitting pipelines during AutoML experiment.
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param y_valid: validation labels to use when fitting pipelines during AutoML experiment.
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param sample_weight_valid:
            The weight to give to each validation sample when running scoring pipelines,
            each row should correspond to a row in X and y data.
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
            or azureml.data.TabularDataset
        :param cv_splits_indices:
            Indices where to split training data for cross validation.
            Each row is a separate cross fold and within each crossfold, provide 2 arrays, t
            he first with the indices for samples to use for training data and the second with the indices to
            use for validation data. i.e [[t1, v1], [t2, v2], ...] where t1 is the training indices for the first cross
            fold and v1 is the validation indices for the first cross fold.
        :type cv_splits_indices: numpy.ndarray
        :param validation_size:
            What percent of the data to hold out for validation when user validation data
            is not specified.
        :type validation_size: float
        :param n_cross_validations: How many cross validations to perform when user validation data is not specified.
        :type n_cross_validations: int
        :param y_min: Minimum value of y for a regression experiment.
        :type y_min: float
        :param y_max: Maximum value of y for a regression experiment.
        :type y_max: float
        :param num_classes: Number of classes in the label data for a classification experiment.
        :type num_classes: int
        :param featurization:
            'auto' / 'off' / FeaturizationConfig
            Indicator for whether featurization step should be done automatically or not,
            or whether customized featurization should be used.
            Note: If the input data is sparse, featurization cannot be turned on.

            Column type is automatically detected. Based on the detected column type
            preprocessing/featurization is done as follows:

            Categorical: Target encoding, one hot encoding, drop high cardinality categories, impute missing values.
            Numeric: Impute missing values, cluster distance, weight of evidence.
            DateTime: Several features such as day, seconds, minutes, hours etc.
            Text: Bag of words, pre-trained Word embedding, text target encoding.

            More details can be found here:
            https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-create-portal-experiments#advanced-preprocessing-options

            To customize featurization step, provide FeaturizationConfig object.
            Customized featurization currently supports blocking a set of transformers, updating column purpose,
            editing transformer parameters, and dropping columns.

            Note: Timeseries features are handled separately when the task type is set to forecasting independent
            of this parameter.
        :type featurization: str or FeaturizationConfig
        :param lag_length: How many rows of historical data to include when preprocessing time series data.
        :type lag_length: int
        :param max_cores_per_iteration: Maximum number of threads to use for a given training iteration.
            This should be less than or equal to the maximum number of cores on the compute target.
        :type max_cores_per_iteration: int
        :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel on an amlcompute
            cluster, on a DSVM, or on Databricks. This should be less than or equal to the number
            of cores on the amlcompute/DSVM or worker nodes on Databricks. If you run multiple
            experiments in parallel on a single amlcompute cluster or DSVM, the sum of the
            max_concurrent_iterations values should be less than or equal to the maximum number of nodes.
            It does not apply to local runs. Formerly concurrent_iterations.
        :type max_concurrent_iterations: int
        :param iteration_timeout_minutes:
            Maximum time in minutes that each iteration can run for before it terminates.
        :type iteration_timeout_minutes: int
        :param mem_in_mb: Maximum memory usage that each iteration can run for before it terminates.
        :type mem_in_mb: int
        :param enforce_time_on_windows:
            flag to enforce time limit on model training at each iteration under windows.
            If running from a python script file (.py) please refer to the documentation for allowing resource limits
            on windows.
        :type enforce_time_on_windows: bool
        :param experiment_timeout_minutes:
            Maximum amount of time in minutes that all iterations combined can take before the
            experiment terminates.
        :type experiment_timeout_minutes: int
        :param experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :type experiment_exit_score: float
        :param enable_early_stopping:
            Flag to enble early termination if the score is not improving in the short term.
        :type enable_early_stopping: bool
        :param blacklist_models: List of algorithms to ignore for AutoML experiment.
        :type blacklist_models: list(str) or list(azureml.train.automl.constants.SupportedModels)
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label.
        :type exclude_nan_labels: bool
        :param verbosity: Verbosity level for AutoML log file.
        :type verbosity: int
        :param enable_tf: Flag to enable/disable Tensorflow algorithms
        :type enable_tf: bool
        :param enable_cache: Flag to enable/disable disk cache for transformed, preprocessed data.
        :type enable_cache: bool
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or automl.client.core.common.constants.PipelineCost
        :param whitelist_models: List of model names to search for AutoML experiment
        :type list(str) or list(azureml.train.automl.constants.SupportedModels)
        :param enable_onnx_compatible_models: Flag to enable/disable enforcing the onnx compatible models.
        :type enable_onnx_compatible_models: bool
        :param enable_voting_ensemble: Flag to enable/disable VotingEnsemble iteration.
        :type enable_voting_ensemble: bool
        :param enable_stack_ensemble: Flag to enable/disable StackEnsemble iteration.
        :type enable_stack_ensemble: bool
        :param time_column_name: The name of your time column.
        :type time_column_name: str
        :param max_horizon: The number of periods out you would like to predict past your training data.
            Periods are inferred from your data.
        :type max_horizon: int
        :param grain_column_names: The names of columns used to group your timeseries.
            It can be used to create multiple series.
        :type grain_column_names: List[str]
        :param drop_column_names: The names of columns to drop.
        :type drop_column_names: List[str]
        :param target_lags: The number of past periods to lag from the target column.
        :type target_lags: int
        :param target_rolling_window_size: The number of past periods used to create a
            rolling window average of the target column.
        :type target_rolling_window_size: int
        :param country_or_region: The country/region used to generate holiday features.
            These should be ISO 3166 two-letter country/region codes (i.e. 'US', 'GB').
        :type country_or_region: str
        :param debug_log: Log file to write debug information to.
        :type debug_log: str
        :param training_data: The training data to be used within the experiment.
            It should contain both training features and label column (optionally a sample weights column).
        :type training_data: pandas.DataFrame or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param validation_data: The validation data to be used within the experiment.
            It should contain both training features and label column (optionally a sample weights column).
        :type validation_data: pandas.DataFrame or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param label_column_name: The name of the label column.
        :type label_column_name: str
        :param weight_column_name: The name of the sample weight column.
        :type weight_column_name: str
        """
        self.user_settings = {}     # type: Dict[str, Any]
        self.fit_params = {}        # type: Dict[str, Any]
        self._run_configuration = None
        self.is_timeseries = False
        blacklist_tf = []           # type: List[str]

        if task not in constants.Tasks.ALL:
            raise ConfigException("Invalid Task: '{0}'. Supported Tasks: "
                                  "{1}".format(task, constants.Tasks.ALL))
        if task == constants.Tasks.CLASSIFICATION:
            # set default metric if not set
            if primary_metric is None:
                primary_metric = constants.Metric.Accuracy
            if y_min is not None or y_max is not None:
                raise ConfigException("Classification tasks do not use"
                                      "'y_min' or 'y_max'")
            if not self.user_settings.get('enable_tf'):
                blacklist_tf = [constants.SupportedModels.Classification.TensorFlowDNNClassifier,
                                constants.SupportedModels.Classification.TensorFlowLinearClassifier]
        else:
            if task == constants.Tasks.FORECASTING:
                self.is_timeseries = True
                task = constants.Tasks.REGRESSION
            if primary_metric is None:
                primary_metric = constants.Metric.NormRMSE
            if num_classes is not None:
                raise ConfigException("Regression tasks do not use 'num_classes'")
            if not self.user_settings.get('enable_tf'):
                blacklist_tf = [constants.SupportedModels.Regression.TensorFlowDNNRegressor,
                                constants.SupportedModels.Regression.TensorFlowLinearRegressor]

        if isinstance(featurization, str):
            featurization = featurization.lower()
            if featurization == FeaturizationConfigMode.Off:
                self.user_settings['featurization'] = FeaturizationConfigMode.Off
                self.user_settings['preprocess'] = False
            elif featurization == FeaturizationConfigMode.Auto:
                self.user_settings['featurization'] = FeaturizationConfigMode.Auto
                self.user_settings['preprocess'] = True
            else:
                raise ConfigException("Invalid Featurization Configuration"
                                      "Must be either '{0}', '{1}' or an instance of FeaturizationConfig."
                                      .format(FeaturizationConfigMode.Off, FeaturizationConfigMode.Auto))
        elif isinstance(featurization, FeaturizationConfig):
            self.user_settings['featurization'] = featurization
            self.user_settings['preprocess'] = True
        else:
            raise ConfigException("Invalid Featurization Configuration"
                                  "Must be either '{0}', '{1}' or an instance of FeaturizationConfig."
                                  .format(FeaturizationConfigMode.Off, FeaturizationConfigMode.Auto))

        # Deprecation of preprocess
        preprocess = kwargs.pop('preprocess', False)
        # TODO: Uncomment logging after notebook changes are made
        # logging.warning("Parameter 'preprocess' will be deprecated. Use 'featurization'")
        if featurization == FeaturizationConfigMode.Off and preprocess:
            # if default featurization mode and preprocess flag is passed in, user is using deprecated flag
            self.user_settings['featurization'] = FeaturizationConfigMode.Auto
            # TODO: deprecate preprocess from automlsettings
            self.user_settings['preprocess'] = preprocess

        self.user_settings["enable_dnn"] = kwargs.get("enable_dnn", False)
        if task == constants.Tasks.CLASSIFICATION \
                and self.user_settings["enable_dnn"] \
                and not self.user_settings['preprocess']:
            self.user_settings['preprocess'] = True
            logging.info("Resetting AutoMLConfig param preprocess=True required by neural nets for classification.")

        # disable tensorflow if module is not present or data is preprocessed outside tf.
        if enable_tf:
            if not AzureAutoMLClient._is_tensorflow_module_present():
                enable_tf = False
                logging.warning("tensorflow module is not installed")
            elif (isinstance(self.user_settings['featurization'], str) and
                  self.user_settings['featurization'] == FeaturizationConfigMode.Auto) or \
                    isinstance(self.user_settings['featurization'], FeaturizationConfig):
                enable_tf = False
                logging.info("tensorflow models are not supported with featurization")

        # validate white list elements are not in black list
        if (not enable_tf or blacklist_models is not None) and whitelist_models is not None:
            blacklist = []
            if not enable_tf:
                blacklist.extend(blacklist_tf)
            if blacklist_models is not None:
                blacklist.extend(blacklist_models)
            if len(blacklist) > 0 and set(whitelist_models).issubset(set(blacklist)):
                raise ConfigException("Can not find models to train, all whitelisted models are also in blacklist")

        for key, value in kwargs.items():
            self.user_settings[key] = value

        self.user_settings['task_type'] = task
        self.user_settings["primary_metric"] = primary_metric
        self.user_settings["compute_target"] = compute_target

        # For backward compatibility if user passes these, keep as is
        self.user_settings['X'] = X
        self.user_settings['y'] = y
        self.user_settings['sample_weight'] = sample_weight
        self.user_settings['X_valid'] = X_valid
        self.user_settings['y_valid'] = y_valid
        self.user_settings['sample_weight_valid'] = sample_weight_valid
        self.user_settings['training_data'] = training_data
        self.user_settings['validation_data'] = validation_data
        self.user_settings['label_column_name'] = label_column_name
        self.user_settings['weight_column_name'] = weight_column_name
        self.user_settings['cv_splits_indices'] = cv_splits_indices
        self.user_settings["num_classes"] = num_classes
        self.user_settings["y_min"] = y_min
        self.user_settings["y_max"] = y_max
        self.user_settings["path"] = path
        self.user_settings["iterations"] = iterations
        self.user_settings["data_script"] = data_script
        self.user_settings["validation_size"] = validation_size
        self.user_settings["n_cross_validations"] = n_cross_validations
        self.user_settings["lag_length"] = lag_length
        self.user_settings["max_cores_per_iteration"] = max_cores_per_iteration
        self.user_settings["max_concurrent_iterations"] = max_concurrent_iterations
        self.user_settings["iteration_timeout_minutes"] = iteration_timeout_minutes
        self.user_settings["mem_in_mb"] = mem_in_mb
        self.user_settings["enforce_time_on_windows"] = enforce_time_on_windows
        self.user_settings["experiment_timeout_minutes"] = experiment_timeout_minutes
        self.user_settings["experiment_exit_score"] = experiment_exit_score
        self.user_settings["enable_early_stopping"] = enable_early_stopping
        self.user_settings["blacklist_models"] = blacklist_models
        self.user_settings["exclude_nan_labels"] = exclude_nan_labels
        self.user_settings["verbosity"] = verbosity
        self.user_settings["enable_tf"] = enable_tf
        self.user_settings["is_timeseries"] = self.is_timeseries
        self.user_settings["enable_cache"] = enable_cache
        self.user_settings["spark_context"] = spark_context
        self.user_settings["enable_subsampling"] = kwargs.get("enable_subsampling", None)
        self.user_settings["subsample_seed"] = kwargs.get("subsample_seed", None)
        self.user_settings["enable_onnx_compatible_models"] = enable_onnx_compatible_models
        self.user_settings["enable_split_onnx_featurizer_estimator_models"] = kwargs.get(
            "enable_split_onnx_featurizer_estimator_models", False)
        self.user_settings["enable_voting_ensemble"] = enable_voting_ensemble
        self.user_settings["enable_stack_ensemble"] = enable_stack_ensemble
        self.user_settings["enable_feature_sweeping"] = kwargs.get("enable_feature_sweeping", True)
        self.user_settings["debug_log"] = debug_log

        # Depracation of autoblacklist
        auto_blacklist = kwargs.get('auto_blacklist')
        if auto_blacklist is not None:
            logging.warning("Parameter 'auto_blacklist' will be deprecated and enabled by default moving forward.'")
            self.user_settings["auto_blacklist"] = auto_blacklist

        # Deprecation of concurrent_iterations
        try:
            concurrent_iterations = kwargs.pop('concurrent_iterations')
            logging.warning("Parameter 'concurrent_iterations' will be deprecated. Use 'max_concurrent_iterations'")
            self.user_settings["max_concurrent_iterations"] = concurrent_iterations
        except KeyError:
            pass

        # Deprecation of max_time_sec
        try:
            max_time_sec = kwargs.pop('max_time_sec')
            logging.warning("Parameter 'max_time_sec' will be deprecated. Use 'iteration_timeout_minutes'")
            self.user_settings["iteration_timeout_minutes"] = math.ceil(max_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_time_sec
        try:
            exit_time_sec = kwargs.pop('exit_time_sec')
            logging.warning("Parameter 'exit_time_sec' will be deprecated. Use 'experiment_timeout_minutes'")
            self.user_settings["experiment_timeout_minutes"] = math.ceil(exit_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_score
        try:
            exit_score = kwargs.pop('exit_score')
            logging.warning("Parameter 'exit_score' will be deprecated. Use 'experiment_exit_score'")
            self.user_settings["experiment_exit_score"] = exit_score
        except KeyError:
            pass

        # Deprecation of blacklist_algos
        try:
            blacklist_algos = kwargs.pop('blacklist_algos')
            logging.warning("Parameter 'blacklist_algos' will be deprecated. Use 'blacklist_models'")
            self.user_settings["blacklist_algos"] = blacklist_algos
        except KeyError:
            pass

            # Deprecation of debug_log
        try:
            debug_log = kwargs.pop('debug_log')
            logging.warning("Parameter 'debug_log' will be deprecated.")
            self.user_settings["debug_log"] = debug_log
        except KeyError:
            pass

        self.user_settings["whitelist_models"] = whitelist_models
        self.user_settings["cost_mode"] = cost_mode

        self._run_configuration = self.user_settings.get('run_configuration', None)

    def _get_remove_fit_params(self, func: 'Callable[..., Optional[Any]]' = AzureAutoMLClient.fit) -> None:
        """
        Remove fit parameters from config.

        Inspects _AzureMLClient.fit() signature and builds a dictionary
        of args to be passed in from settings, using defauls as required
        and removes these params from settings

        :returns:
        """
        if not self.fit_params:
            fit_signature = inspect.signature(func)
            for k, v in fit_signature.parameters.items():
                # skip parameters
                if k in ['self', 'run_configuration', 'data_script', 'show_output']:
                    continue

                default_val = v.default

                # Parameter.empty is returned for any parameters without a default
                # we will require these in settings
                if default_val is inspect.Parameter.empty:
                    try:
                        self.fit_params[k] = self.user_settings.pop(k)
                    except KeyError:
                        raise ConfigException("To submit an experiment you will need"
                                              " to provide a value for '{0}'".format(k))
                else:
                    self.fit_params[k] = self.user_settings.pop(k, default_val)

        # overwrite default run_config with user provided or None
        self.fit_params['run_configuration'] = self._run_configuration

    def _validate_config_settings(self, workspace: Optional[Workspace] = None) -> None:
        """Validate the configuration attributes."""
        # TODO: We have duplicate code for handling run configuration; it should be refactored
        # assert we have a run_config, if not create default
        # and assume default config
        if self._run_configuration is None:
            if 'run_configuration' not in self.user_settings.keys():
                self._run_configuration = RunConfiguration()
            elif isinstance(self.user_settings['run_configuration'], str):
                path = self.user_settings.get('path', '.')
                self._run_configuration = RunConfiguration.load(path=path,
                                                                name=self.user_settings['run_configuration'])
            else:
                self._run_configuration = self.user_settings['run_configuration']

        # ensure compute target is set
        if 'compute_target' in self.user_settings and self.user_settings['compute_target'] is not None:
            self._run_configuration.target = self.user_settings['compute_target']
            if self.user_settings['compute_target'] != constants.ComputeTargets.LOCAL and \
                    self.user_settings['compute_target'] == constants.ComputeTargets.AMLCOMPUTE:
                self._run_configuration.environment.docker.enabled = True
        else:
            self.user_settings['compute_target'] = self._run_configuration.target

        if self._run_configuration.framework.lower() != 'python':
            raise ConfigException('AutoML requires the run configuration framework to be set to "Python".')

        # remove compute target from setting
        self.user_settings.pop('run_configuration', None)

        has_training_input_dprep_obj = False
        has_training_input_pandas_obj = False
        has_feature_label_input = False  # for the case when features & label columns are separated
        has_single_dataset_input = False  # for the case the input is features + label combined
        for key in ['X', 'y', 'sample_weight', 'X_valid', 'y_valid', 'sample_weight_valid',
                    'cv_splits_indices', 'training_data', 'validation_data']:
            value = self.user_settings.get(key)
            if value is not None:
                if key != 'cv_splits_indices':
                    if key in ['training_data', 'validation_data']:
                        has_single_dataset_input = True
                    else:
                        has_feature_label_input = True
                    if dataprep_utilities.is_dataflow(value) or dataset_utilities.is_dataset(value):
                        has_training_input_dprep_obj = True
                    else:
                        has_training_input_pandas_obj = True
                else:
                    cv_splits_indices = value
                    if not isinstance(cv_splits_indices, list):
                        raise ConfigException("cv_splits_indices should be a list")

                    for split in cv_splits_indices:
                        if dataprep_utilities.is_dataflow(split):
                            has_training_input_dprep_obj = True
                        else:
                            has_training_input_pandas_obj = True

        if has_training_input_dprep_obj and has_training_input_pandas_obj:
            raise ConfigException("A mix of dprep and pandas objects provided. "
                                  "Please provide either all dataflow or all pandas objects")
        if has_single_dataset_input:
            if has_feature_label_input:
                raise ConfigException("The input data can either be combined (Features & Label column) or \
                            separate Features dataset and Label column.")
            if self.user_settings['label_column_name'] is None:
                raise ConfigException("When a single dataset which combines Features & Label columns is used as input, \
                            `label_column_name` parameter is mandatory.")

        compute_target = self.user_settings['compute_target']
        # The compute target here can either be str or ComputeTarget class, need a conversion here.
        if compute_target is not None and not isinstance(compute_target, str):
            compute_target = compute_target.name

        if compute_target != constants.ComputeTargets.LOCAL:
            data_script_provided = self.user_settings.get('data_script') is not None
            if not data_script_provided and not has_training_input_dprep_obj:
                raise ConfigException("You must provide a 'data_script'"
                                      " or provide data with `azureml.dataprep.Dataflow`, `azureml.core.Dataset`,"
                                      " or `azureml.data.DatasetDefinition"
                                      " to create a remote run")
            if workspace is not None and compute_target is not None:
                all_compute_targets = workspace.compute_targets
                if compute_target not in all_compute_targets:
                    raise ConfigException("The compute target {} does not exist in the selected workspace. "
                                          "Please attach compute or use a different compute.".format(compute_target))
                elif all_compute_targets[compute_target].provisioning_state != ProvisioningState.succeeded.value:
                    raise ConfigException(
                        "The compute target {} is in the provisioning state {}. Please check your compute status "
                        "or wait for the compute creation to complete.".format(
                            compute_target,
                            all_compute_targets[compute_target].provisioning_state
                        )
                    )
                else:
                    # ensure vm size is set
                    self.user_settings['vm_type'] = all_compute_targets[compute_target].vm_size

        if (self.user_settings.get('training_data', None) is not None and
            self.user_settings.get('label_column_name', None) is None) or \
                (self.user_settings.get('label_column_name', None) is not None and
                 self.user_settings.get('training_data', None) is None):
            raise ConfigException("Please provide 'label_column_name' if 'training_data' is provided in "
                                  "AutoMLConfig or vice versa.")

        if self.user_settings.get('validation_data', None) is not None and \
                (self.user_settings.get('training_data', None) is None or
                 self.user_settings.get('label_column_name', None) is None):
            raise ConfigException("Please provide 'training_data' and 'label_column_name' "
                                  "if 'validation_data' is provided in AutoMLConfig ")
