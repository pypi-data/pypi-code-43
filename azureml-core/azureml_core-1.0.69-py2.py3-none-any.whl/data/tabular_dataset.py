# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for representing data in a tabular format by parsing the provided file or list of files.

For more information, see the article [Add & register
datasets](https://docs.microsoft.com/azure/machine-learning/service/how-to-create-register-datasets).
To get started working with a tabular dataset, see https://aka.ms/tabulardataset-samplenotebook.
"""

import os
import sys
from datetime import datetime
from uuid import uuid4
from backports import tempfile
from shutil import copyfile
from azureml.data._dataset import _Dataset
from azureml.data._loggerfactory import track, _LoggerFactory, collect_datasets_usage
from azureml.data.constants import _PUBLIC_API, _DATASET_PROP_TIMESTAMP_FINE, _DATASET_PROP_TIMESTAMP_COARSE, \
    _LOCAL_COMPUTE, _ACTION_TYPE_PROFILE, _LEGACY_DATASET_ID, _PROFILE_RUN_SUBMIT_ACTIVITY
from azureml.data.dataset_error_handling import _validate_has_data, _validate_has_columns, _try_execute
from azureml.data._dataprep_helper import dataprep, get_dataflow_for_execution
from azureml.data._dataset_rest_helper import _restclient, _custom_headers
from azureml.exceptions import DatasetTimestampMissingError
from azureml._restclient.models.action_request_dto import ActionRequestDto

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class TabularDataset(_Dataset):
    """Represents a tabular dataset to use in Azure Machine Learning service.

    A TabularDataset defines a series of lazily-evaluated, immutable operations to load data from the
    data source into tabular representation. Data is not loaded from the source until TabularDataset
    is asked to deliver data.

    TabularDataset is created using methods like
    :func:`azureml.data.dataset_factory.TabularDatasetFactory.from_delimited_files` from the
    :class:`azureml.data.dataset_factory.TabularDatasetFactory` class.

    For more information, see the article `Add & register
    datasets <https://docs.microsoft.com/azure/machine-learning/service/how-to-create-register-datasets>`_.
    To get started working with a tabular dataset, see https://aka.ms/tabulardataset-samplenotebook.

    .. remarks::

        A TabularDataset can be created from CSV, TSV, Parquet files, or SQL query using the ``from_*``
        methods of the :class:`azureml.data.dataset_factory.TabularDatasetFactory` class. You can
        perform subsetting operations on a TabularDataset like splitting, skipping, and filtering records.
        The result of subsetting is always one or more new TabularDataset objects.

        You can also convert a TabularDataset into other formats like a pandas DataFrame.
        The actual data loading happens when TabularDataset is asked to deliver the data into another
        storage mechanism (e.g. a Pandas Dataframe, or a CSV file).

        TabularDataset can be used as input of an experiment run. It can also be registered to workspace
        with a specified name and be retrieved by that name later.
    """

    def __init__(self):
        """Initialize a TabularDataset object.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.TabularDatasetFactory` class.
        """
        super().__init__()

    @property
    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def timestamp_columns(self):
        """Return the timestamp columns.

        :return: The column names for fine_grain_timestamp and coarse_grain_timestamp defined for the dataset.
        :rtype: (str, str)
        """
        fine_grain_timestamp = self._properties.get(_DATASET_PROP_TIMESTAMP_FINE, None)
        coarse_grain_timestamp = self._properties.get(_DATASET_PROP_TIMESTAMP_COARSE, None)
        return (fine_grain_timestamp, coarse_grain_timestamp)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def with_timestamp_columns(self, fine_grain_timestamp, coarse_grain_timestamp=None, validate=False):
        """Define timestamp columns for the dataset.

        .. remarks::

            The method defines columns to be used as timestamps. Timestamp columns on a dataset make it possible
            to treat the data as time-series data and enable additional capabilities. When a dataset has
            both ``fine_grain_timestamp`` and ``coarse_grain_timestamp defined`` specified, the two columns
            should represent the same timeline.

        :param fine_grain_timestamp: The name of column as fine grain timestamp. Use None to clear it.
        :type fine_grain_timestamp: str
        :param coarse_grain_timestamp: The name of column coarse grain timestamp (optional). The default is None
            (clear).
        :type coarse_grain_timestamp: str
        :param validate: Indicates whether to validate if specified columns exist in dataset. The default is False.
            Validation requires that the data source is accessible from the current compute.
        :type validate: bool
        :return: Returns a new TabularDataset with timestamp columns defined.
        :rtype: azureml.data.TabularDataset
        """
        if not fine_grain_timestamp and coarse_grain_timestamp:
            raise ValueError('Cannot assign coarse_grain_timestamp separately while fine_grain_timestamp is None.')
        if fine_grain_timestamp and fine_grain_timestamp == coarse_grain_timestamp:
            raise ValueError('coarse_grain_timestamp cannot be the same as fine_grain_timestamp.')
        if validate:
            self._validate_timestamp_columns([fine_grain_timestamp, coarse_grain_timestamp])

        dataset = TabularDataset._create(self._dataflow, self._properties, telemetry_info=self._telemetry_info)

        if fine_grain_timestamp:
            dataset._properties[_DATASET_PROP_TIMESTAMP_FINE] = fine_grain_timestamp
        else:
            if _DATASET_PROP_TIMESTAMP_FINE in self._properties:
                del dataset._properties[_DATASET_PROP_TIMESTAMP_FINE]

        if coarse_grain_timestamp:
            dataset._properties[_DATASET_PROP_TIMESTAMP_COARSE] = coarse_grain_timestamp
        else:
            if _DATASET_PROP_TIMESTAMP_COARSE in self._properties:
                del dataset._properties[_DATASET_PROP_TIMESTAMP_COARSE]
        return dataset

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def to_pandas_dataframe(self):
        """Load all records from the dataset into a pandas DataFrame.

        :return: Returns a pandas DataFrame.
        :rtype: pandas.DataFrame
        """
        dataflow = get_dataflow_for_execution(self._dataflow, 'to_pandas_dataframe', 'TabularDataset')
        df = _try_execute(dataflow.to_pandas_dataframe)
        import pandas
        if not isinstance(df, pandas.DataFrame):
            # TODO: remove this check once it is fixed in dprep to return `DataFrame({})` rather than `DataFrame.empty`
            return pandas.DataFrame({})
        return df

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def to_spark_dataframe(self):
        """Load all records from the dataset into a Spark DataFrame.

        :return: Returns a Spark DataFrame.
        :rtype: pyspark.sql.DataFrame
        """
        dataflow = get_dataflow_for_execution(self._dataflow, 'to_spark_dataframe', 'TabularDataset')
        return _try_execute(dataflow.to_spark_dataframe)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def skip(self, count):
        """Skip records from top of the dataset by the specified count.

        :param count: The number of records to skip.
        :type count: int
        :return: Returns a new TabularDataset object representing a dataset with records skipped.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(
            self._dataflow.skip(count), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def take(self, count):
        """Take a sample of records from top of the dataset by the specified count.

        :param count: The number of records to take.
        :type count: int
        :return: Returns a new TabularDataset object representing the sampled dataset.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(
            self._dataflow.take(count), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def take_sample(self, probability, seed=None):
        """Take a random sample of records in the dataset approximately by the probability specified.

        :param probability: The probability of a record being included in the sample.
        :type probability: float
        :param seed: Optional seed to use for the random generator.
        :type seed: int
        :return: Returns a new TabularDataset object representing the sampled dataset.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(
            self._dataflow.take_sample(probability, seed), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def random_split(self, percentage, seed=None):
        """Split records in the dataset into two parts randomly and approximately by the percentage specified.

        :param percentage: The approximate percentage to split the Dataflow by. This must be a number between
            0.0 and 1.0.
        :type percentage: float
        :param seed: Optional seed to use for the random generator.
        :type seed: int
        :return: Returns a tuple of new TabularDataset objects representing the two datasets after the split.
        :rtype: (azureml.data.TabularDataset, azureml.data.TabularDataset)
        """
        dataflow1, dataflow2 = self._dataflow.random_split(percentage, seed)
        return (
            TabularDataset._create(dataflow1, self._properties, telemetry_info=self._telemetry_info),
            TabularDataset._create(dataflow2, self._properties, telemetry_info=self._telemetry_info)
        )

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def keep_columns(self, columns, validate=False):
        """Keep the specified columns and drops all others from the dataset.

        :param columns: The name or a list of names for the columns to keep.
        :type columns: str or builtin.list[str]
        :param validate: Indicates whether to validate if data can be loaded from the returned dataset.
            The default is True. Validation requires that the data source is accessible from current compute.
        :type validate: bool
        :return: Returns a new TabularDataset object for dataset with only the specified columns kept.
        :rtype: azureml.data.TabularDataset
        """
        for col in list(filter(lambda x: x is not None, self.timestamp_columns)):
            if col not in columns:
                error_message = "Column {} should be included because it's a timestamp column".format(col)
                raise ValueError(error_message)

        dataflow = self._dataflow.keep_columns(columns, validate_column_exists=False)
        if validate:
            _validate_has_data(dataflow,
                               ('Cannot load any data from the dataset with only columns {} kept. ' +
                                'Make sure the specified columns exist in the current dataset.')
                               .format(columns if isinstance(columns, list) else [columns]))
        return TabularDataset._create(dataflow, self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def drop_columns(self, columns):
        """Drop the specified columns from the dataset.

        :param columns: The name or a list of names for the columns to drop.
        :type columns: str or builtin.list[str]
        :return: Returns a new TabularDataset object for dataset with the specified columns dropped.
        :rtype: azureml.data.TabularDataset
        """
        for col in list(filter(lambda x: x is not None, self.timestamp_columns)):
            if col in columns:
                error_message = "Column {} should not be dropped because it's a timestamp column. " \
                                "Please exclude it or use with_timestamp_columns with value None to reset it " \
                                "before dropping columns.".format(col)
                raise ValueError(error_message)

        return TabularDataset._create(
            self._dataflow.drop_columns(columns), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def to_parquet_files(self):
        """Convert the current dataset into a FileDataset containing Parquet files.

        The resulting dataset will contain one or more Parquet files, each corresponding to a partition of data
        from the current dataset. These files are not materialized until they are downloaded or read from.

        :return: Returns a new FileDataset object with a set of Parquet files containing the data in this dataset.
        :rtype: azureml.data.FileDataset
        """
        from azureml.data.file_dataset import FileDataset
        parquet_dataflow = self._dataflow.to_parquet_streams()
        return FileDataset._create(parquet_dataflow, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def to_csv_files(self, separator=','):
        """Convert the current dataset into a FileDataset containing CSV files.

        The resulting dataset will contain one or more CSV files, each corresponding to a partition of data
        from the current dataset. These files are not materialized until they are downloaded or read from.

        :param separator: The separator to use to separate values in the resulting file.
        :type separator: str
        :return: Returns a new FileDataset object with a set of CSV files containing the data in this dataset.
        :rtype: azureml.data.FileDataset
        """
        from azureml.data.file_dataset import FileDataset
        csv_dataflow = self._dataflow.to_csv_streams(separator=separator)
        return FileDataset._create(csv_dataflow, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def time_before(self, end_time, include_boundary=False):
        """Filter TabularDataset with time stamp columns before a specified end time.

        :param end_time: Upper bound for filtering data.
        :type end_time: datetime.datetime
        :param include_boundary: Indicate if the row associated with the boundary time (``end_time``) should be
            included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered dataset.
        :rtype: azureml.data.TabularDataset
        """
        return self._time_filter(self.time_before.__name__,
                                 upper_bound=end_time, include_boundary=include_boundary)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def time_after(self, start_time, include_boundary=False):
        """Filter TabularDataset with time stamp columns after a specified start time.

        :param start_time: The lower bound for filtering data.
        :type start_time: datetime.datetime
        :param include_boundary: Indicate if the row associated with the boundary time (``start_time``) should be
            included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered dataset.
        :rtype: azureml.data.TabularDataset
        """
        return self._time_filter(self.time_after.__name__,
                                 lower_bound=start_time, include_boundary=include_boundary)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def time_recent(self, time_delta, include_boundary=False):
        """Filter TabularDataset to contain only the specified duration (amount) ofrecent data.

        :param time_delta: The duration (amount) of recent data to retrieve.
        :type time_delta: datetime.timedelta
        :param include_boundary: Indicate if the row associated with the boundary time (``time_delta``)
            should be included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered dataset.
        :rtype: azureml.data.TabularDataset
        """
        start_time = datetime.now() - time_delta
        return self._time_filter(self.time_recent.__name__,
                                 lower_bound=start_time, include_boundary=include_boundary)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def time_between(self, start_time, end_time, include_boundary=False):
        """Filter TabularDataset between a specified start and end time.

        :param start_time: The Lower bound for filtering data.
        :type start_time: datetime.datetime
        :param end_time: The upper bound for filtering data.
        :type end_time: datetime.datetime
        :param include_boundary: Indicate if the row associated with the boundary time (``start_end`` and
            ``end_time``) should be included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered dataset.
        :rtype: azureml.data.TabularDataset
        """
        return self._time_filter(self.time_between.__name__,
                                 lower_bound=start_time, upper_bound=end_time, include_boundary=include_boundary)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'})
    def _submit_profile_run(self, compute_target, workspace=None):
        """Submit an experimentation run to calculate data profile.

        :param compute_target: The compute to use for data profile calculation. Specify 'local' to use local compute.
        :type compute_target: str or azureml.core.compute.ComputeTarget
        :param workspace: The workspace to submit profile run. Defaults to the workspace of this dataset.
        :type workspace: azureml.core.Workspace
        :return: The submitted profile run.
        :rtype: azureml.data._dataset_profile_run._DatasetProfileRun
        """
        from azureml.core import Experiment, ComputeTarget, RunConfiguration, ScriptRunConfig
        from azureml.data._dataset_profile_run import DatasetProfileRun

        workspace = self._ensure_workspace(workspace)
        if isinstance(compute_target, ComputeTarget):
            compute_target = compute_target.name
        request_dto = ActionRequestDto(
            action_type=_ACTION_TYPE_PROFILE,
            saved_dataset_id=self._ensure_saved(workspace),
            compute_target=compute_target)
        collect_datasets_usage(
            _get_logger(), _PROFILE_RUN_SUBMIT_ACTIVITY, [self], workspace, compute_target)
        action_dto = _restclient(workspace).dataset.submit_action(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id=_LEGACY_DATASET_ID,
            request=request_dto,
            custom_headers=_custom_headers)
        if compute_target == _LOCAL_COMPUTE:
            with tempfile.TemporaryDirectory() as temp_dir:
                script = os.path.join(temp_dir, 'run_dataset_action.py')
                copyfile(os.path.join(__file__, '..', '_run_dataset_action.py'), script)
                run_config = RunConfiguration(
                    script=script,
                    arguments=[action_dto.dataset_id, action_dto.action_id, action_dto.dataflow_artifact_id],
                    framework='Python')
                run_config.environment.python.user_managed_dependencies = True
                run_config.environment.python.interpreter_path = sys.executable
                script_run = ScriptRunConfig(source_directory=temp_dir, run_config=run_config)
                experiment = Experiment(workspace, 'dataset_unregistered_datasets')
                run = experiment.submit(script_run, run_id='dataset_' + str(uuid4()))
                run_id = run.id
        else:
            experiment = Experiment(workspace, action_dto.experiment_name)
            run_id = action_dto.run_id
        return DatasetProfileRun(experiment, run_id, action_dto.action_id)

    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'})
    def _get_latest_profile(self, workspace=None):
        """Get data profile from the latest profile run submitted for this or the same dataset in the workspace.

        :param workspace: The workspace where profile run was submitted. Defaults to the workspace of this dataset.
        :type workspace: azureml.core.Workspace
        :return: A tuple of values. The first value is the profile result from the latest profile run. It will be None
            if there was no profile run completed before. The second value is a flag indicating whether the profile
            matches current data:
                - if the data source change cannot be detected, the flag will be None;
                - if the data source was changed after submitting the profile run, the flag will be False;
                - otherwise, the profile matches current data, and the flag will be True.
        :rtype: (azureml.dataprep.DataProfile, bool)
        """
        from azureml.data._dataset_profile_run import _profile_from_action

        workspace = self._ensure_workspace(workspace)
        request_dto = ActionRequestDto(
            action_type=_ACTION_TYPE_PROFILE,
            saved_dataset_id=self._ensure_saved(workspace))
        action_result_dto = _restclient(workspace).dataset.get_action_result(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            dataset_id=_LEGACY_DATASET_ID,
            request=request_dto,
            custom_headers=_custom_headers)
        if action_result_dto.is_up_to_date_error:
            raise RuntimeError(action_result_dto.is_up_to_date_error)
        return _profile_from_action(workspace, action_result_dto)

    def _time_filter(self, method, lower_bound=None, upper_bound=None, include_boundary=False):
        exception_message = 'Cannot perform time-series filter `{}` on dataset without timestamp columns defined.' \
                            'Please use `with_timestamp_columns` to enable time-series capabilities'.format(method)

        if self._properties is None \
                or _DATASET_PROP_TIMESTAMP_FINE not in self._properties \
                or self._properties[_DATASET_PROP_TIMESTAMP_FINE] is None:
            raise DatasetTimestampMissingError(error_details=exception_message)

        col_fine_timestamp = self._properties[_DATASET_PROP_TIMESTAMP_FINE]
        col_coarse_timestamp = None
        if _DATASET_PROP_TIMESTAMP_COARSE in self._properties \
                and self._properties[_DATASET_PROP_TIMESTAMP_COARSE] is not None:
            col_coarse_timestamp = self._properties[_DATASET_PROP_TIMESTAMP_COARSE]

        # validate column type are datetime
        self._validate_timestamp_columns([col_fine_timestamp, col_coarse_timestamp])

        dataflow = self._dataflow

        # base filter, will enrich filters in following steps.
        from azureml.dataprep import Expression
        filters = Expression(dataflow[col_fine_timestamp] is not None)

        if lower_bound is not None:
            # coarse timestamp may not be assigned.
            if col_coarse_timestamp is not None:
                filter_coarse_lower = dataflow[col_coarse_timestamp] >= lower_bound if include_boundary \
                    else dataflow[col_coarse_timestamp] > lower_bound
                filters &= filter_coarse_lower
            # fine timestamp is guaranteed to be there.
            filter_fine_lower = dataflow[col_fine_timestamp] >= lower_bound if include_boundary \
                else dataflow[col_fine_timestamp] > lower_bound
            filters &= filter_fine_lower

        if upper_bound is not None:
            # coarse timestamp may not be assigned.
            if col_coarse_timestamp is not None:
                filter_coarse_upper = dataflow[col_coarse_timestamp] <= upper_bound if include_boundary \
                    else dataflow[col_coarse_timestamp] < upper_bound
                filters &= filter_coarse_upper
            # fine timestamp is guaranteed to be there.
            filter_fine_upper = dataflow[col_fine_timestamp] <= upper_bound if include_boundary \
                else dataflow[col_fine_timestamp] < upper_bound
            filters &= filter_fine_upper

        result = dataflow.filter(filters)

        return TabularDataset._create(result, self._properties, telemetry_info=self._telemetry_info)

    def _validate_timestamp_columns(self, columns_list):
        FieldType = dataprep().api.engineapi.typedefinitions.FieldType
        columns = list(filter(lambda col: col is not None, columns_list))
        _validate_has_columns(self._dataflow, columns, [FieldType.DATE for c in columns])

    def _ensure_workspace(self, workspace):
        if workspace is not None:
            return workspace
        if self._registration is None or self._registration.workspace is None:
            raise RuntimeError(
                'The dataset does not belong to a workspace. Please pass in the workspace from argument.')
        return self._registration.workspace
