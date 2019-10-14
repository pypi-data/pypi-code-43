# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the data drift logic between two datasets, relies on the DataSets API."""

import warnings
from datetime import timezone, datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from azureml._restclient.exceptions import ServiceException
from azureml.core import Datastore, Dataset, Experiment, Run
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.workspace import Workspace
from azureml.exceptions import ComputeTargetException
from azureml.pipeline.core import Schedule
from msrest.exceptions import HttpOperationError

from azureml.datadrift import alert_configuration
from azureml.datadrift._logging._telemetry_logger import _TelemetryLogger
from azureml.datadrift._logging._telemetry_logger_context_adapter import \
    _TelemetryLoggerContextAdapter
from azureml.datadrift._restclient import DataDriftClient
from azureml.datadrift._restclient.api_versions import PUBLICPREVIEW
from azureml.datadrift._restclient.models import (AlertConfiguration, CreateDataDriftDto, CreateDataDriftRunDto,
                                                  UpdateDataDriftDto)
from azureml.datadrift._result_handler import _get_metrics_path, all_outputs, show
from azureml.datadrift._schedule_state import ScheduleState
from azureml.datadrift._utils.constants import (
    COMPUTE_TARGET_TYPE_AML, RUN_TYPE_ADHOC, RUN_TYPE_BACKFILL, DATADRIFT_TYPE_DATASET,
    DATADRIFT_TYPE_MODEL, DATADRIFT_CONSTRUCTOR, DATADRIFT_CREATE, DATADRIFT_CREATE_FROM_MODEL,
    DATADRIFT_CREATE_FROM_DATASET, DATADRIFT_GET, DATADRIFT_GET_BY_NAME, DATADRIFT_LIST,
    DATADRIFT_RUN, DATADRIFT_ENABLE_SCHEDULE, DATADRIFT_DISABLE_SCHEDULE, DATADRIFT_UPDATE,
    DATADRIFT_BACKFILL, DATADRIFT_GET_OUTPUT, DATADRIFT_SHOW
)
from ._utils.parameter_validator import ParameterValidator

module_logger = _TelemetryLogger.get_telemetry_logger(__name__)

DEFAULT_COMPUTE_TARGET_NAME = "datadrift-server"
DEFAULT_VM_SIZE = "STANDARD_D2_V2"
DEFAULT_VM_MAX_NODES = 4
DEFAULT_DRIFT_THRESHOLD = 0.2


class DataDriftDetector:
    """Class for AzureML DataDriftDetector.

    DataDriftDetector class provides set of convenient APIs to identify any drifting between given training
    and/or scoring datasets for a model. A DataDriftDetector object is created with a workspace, a model name
    and version, list of services, and optional tuning parameters. A DataDriftDetector task can be scheduled
    using enable_schedule() API and/or a one time task can be submitted using run() method.
    """

    def __init__(self, workspace, model_name, model_version):
        """Datadriftdetector constructor.

        The DataDriftDetector constructor is used to retrieve a cloud representation of a DataDriftDetector object
        associated with the provided workspace. Must provide model_name and model_version.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :return: A DataDriftDetector object
        :rtype: DataDriftDetector
        """
        if workspace is ... or model_name is ... or model_version is ...:
            # Instantiate an empty DataDriftDetector object. Will be initialized by DataDriftDetector.get()
            return

        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

        self._logger = _TelemetryLoggerContextAdapter(module_logger, log_context)

        workspace = ParameterValidator.validate_workspace(workspace)
        model_name = ParameterValidator.validate_model_name(model_name)
        model_version = ParameterValidator.validate_model_version(model_version)
        _TelemetryLogger.log_event(DATADRIFT_CONSTRUCTOR, **log_context)
        with _TelemetryLogger.log_activity(self._logger, activity_name="constructor") as logger:

            try:
                dd_list = DataDriftDetector._get_datadrift_list(workspace, model_name=model_name,
                                                                model_version=model_version, logger=logger)
                if len(dd_list) > 1:
                    error_msg = "Multiple DataDriftDetector objects for: {} {} {}".format(workspace, model_name,
                                                                                          model_version)
                    logger.error(error_msg)
                    raise LookupError(error_msg)
                elif len(dd_list) == 1:
                    dto = dd_list[0]
                    self._initialize(workspace, dto)
                else:
                    error_msg = "Could not find DataDriftDetector object for: {} {} {}".format(workspace, model_name,
                                                                                               model_version)
                    logger.error(error_msg)
                    raise KeyError(error_msg)
            except HttpOperationError or KeyError:
                # DataDriftDetector object doesn't exist for model_name and model_version, create one instead
                logger.error("DataDriftDetector object for model_name: {}, model_version: {} doesn't exist. "
                             "Create with DatadriftDetector.create()".format(model_name, model_version))
                raise

    def _initialize(self, workspace, client_dto):
        r"""Class DataDriftDetector Constructor helper.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param client_dto: DataDrift Client DTO object from service call
        :type client_dto: azureml.datadrift._restclient.models.DataDriftDto
        :return: A DataDriftDetector object
        :rtype: DataDriftDetector
        """
        self._workspace = workspace
        self._frequency = client_dto.frequency
        self._schedule_start = client_dto.schedule_start_time
        self._schedule_id = client_dto.schedule_id
        self._interval = client_dto.interval
        self._state = client_dto.state
        self._alert_config = client_dto.alert_configuration
        self._type = client_dto.type if client_dto.type else DATADRIFT_TYPE_MODEL
        self._id = client_dto.id
        self._model_name = client_dto.model_name
        self._model_version = client_dto.model_version
        self._services = client_dto.services
        self._compute_target_name = client_dto.compute_target_name
        self._drift_threshold = client_dto.drift_threshold
        self._baseline_dataset_id = client_dto.base_dataset_id
        self._target_dataset_id = client_dto.target_dataset_id
        self._feature_list = client_dto.features
        self._latency = client_dto.job_latency
        self._name = client_dto.name

        # Set alert configuration
        self._alert_config = alert_configuration.AlertConfiguration(
            client_dto.alert_configuration.email_addresses) if client_dto.alert_configuration else None

        # Instantiate service client
        self._client = DataDriftClient(self.workspace.service_context)

        if not hasattr(self, '_logger'):
            log_context = {
                'workspace_name': workspace.name, 'model_name': client_dto.model_name,
                'model_version': client_dto.model_version, 'dd_id': client_dto.id,
                'workspace_id': workspace._workspace_id, 'workspace_location': workspace.location,
                'subscription_id': workspace.subscription_id}

            self._logger = _TelemetryLoggerContextAdapter(module_logger, log_context)

    def __repr__(self):
        """Return the string representation of a DataDriftDetector object.

        :return: DataDriftDetector object string
        :rtype: str
        """
        return str(self.__dict__)

    @property
    def workspace(self):
        """Get the workspace of the DataDriftDetector object.

        :return: Workspace object
        :rtype: azureml.core.workspace.Workspace
        """
        return self._workspace

    @property
    def name(self):
        """Get the name of the DataDriftDetector object.

        :return: DataDriftDetector name
        :rtype: str
        """
        return self._name

    @property
    def model_name(self):
        """Get the model name associated with the DataDriftDetector object.

        :return: Model name
        :rtype: str
        """
        return self._model_name

    @property
    def model_version(self):
        """Get the model version associated with the DataDriftDetector object.

        :return: Model version
        :rtype: int
        """
        return self._model_version

    @property
    def services(self):
        """Get the list of services attached to the DataDriftDetector object.

        :return: List of service names
        :rtype: builtin.list[str]
        """
        return self._services

    @property
    def compute_target_name(self):
        """Get the Compute Target name attached to the DataDriftDetector object.

        :return: Compute Target name
        :rtype: str
        """
        return self._compute_target_name

    @property
    def frequency(self):
        """Get the frequency of the DataDriftDetector schedule.

        :return: String of either "Day", "Week" or "Month"
        :rtype: str
        """
        return self._frequency

    @property
    def interval(self):
        """Get the interval of the DataDriftDetector schedule.

        :return: Integer value of time unit
        :rtype: int
        """
        return self._interval

    @property
    def feature_list(self):
        """Get the list of whitelisted features for the DataDriftDetector object.

        :return: List of feature names
        :rtype: builtin.list[str]
        """
        return self._feature_list

    @property
    def drift_threshold(self):
        """Get the drift threshold for the DataDriftDetector object.

        :return: Drift threshold
        :rtype: float
        """
        return self._drift_threshold

    @property
    def baseline_dataset(self):
        """Get the baseline dataset.

        :return: Dataset type of the baseline dataset
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset.get_by_id(self.workspace, self._baseline_dataset_id)

    @property
    def target_dataset(self):
        """Get the target dataset.

        :return: Dataset type of the baseline dataset
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset.get_by_id(self.workspace, self._target_dataset_id)

    @property
    def schedule_start(self):
        """Get the start time of the schedule.

        :return: Datetime object of schedule start time in UTC
        :rtype: datetime.datetime
        """
        return self._schedule_start

    @property
    def alert_config(self):
        """Get the alert configuration for the DataDriftDetector object.

        :return: AlertConfiguration object.
        :rtype: azureml.datadrift.AlertConfiguration
        """
        return self._alert_config

    @property
    def state(self):
        """Denotes the state of the DataDrift schedule.

        :return: One of 'Disabled', 'Enabled', 'Disabling', 'Enabling'
        :rtype: str
        """
        return self._state

    @property
    def enabled(self):
        """Get the boolean value for whether the DataDriftDetector is enabled or not.

        :return: Boolean value; true for enabled
        :rtype: bool
        """
        return self._state == ScheduleState.Enabled.name

    @property
    def latency(self):
        """Get the latency of the DataDriftDetector schedule jobs (in hours).

        :return: Number of hours
        :rtype: int
        """
        return self._latency

    @property
    def drift_type(self):
        """Get the type of the DataDriftDetector, either 'ModelBased' or 'DatasetBased'.

        :return: Type of DataDriftDetector
        :rtype: str
        """
        return self._type

    @staticmethod
    def create(workspace, model_name, model_version, services, compute_target_name=None,
               frequency=None, interval=None, feature_list=None, schedule_start=None, alert_config=None,
               drift_threshold=None):
        r"""Create a new DataDriftDetector object in the Azure Machine Learning Workspace.

        Throws an exception if a DataDriftDetector for the same model_name and model_version already exists in the
        workspace.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :param services: Optional, list of AzureML webservices to run DataDriftDetector schedule
        :type services: builtin.list[str]
        :param compute_target_name: Optional, AzureML ComputeTarget name; DataDriftDetector will create one if none
                                    specified
        :type compute_target_name: str
        :param frequency: Optional, how often the pipeline is run. Supports "Day", "Week" or "Month"
        :type frequency: str
        :param interval: Optional, how often the pipeline runs based on frequency. i.e. If frequency = "Day" and \
                         interval = 2, the pipeline will run every other day
        :type interval: int
        :param feature_list: Optional, whitelisted features to run the datadrift detection on. DataDriftDetector jobs
                             will run on all features if no feature_list is specified.
        :type feature_list: builtin.list[str]
        :param schedule_start: Optional, start time of data drift schedule in UTC. Current time used if None specified
        :type schedule_start: datetime.datetime
        :param alert_config: Optional, configuration object for DataDriftDetector alerts
        :type alert_config: azureml.datadrift.AlertConfiguration
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on. Defaults to 0.2
        :type drift_threshold: float
        :return: A DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.create')
        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        _TelemetryLogger.log_event(DATADRIFT_CREATE, **log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="datadriftdetector.create") as logger:
            logger.warning("Deprecated, please use create_from_model(). Will be removed in future releases.")
            return DataDriftDetector.create_from_model(workspace, model_name, model_version, services,
                                                       compute_target_name, frequency, interval, feature_list,
                                                       schedule_start, alert_config, drift_threshold)

    @staticmethod
    def create_from_model(workspace, model_name, model_version, services, compute_target_name=None,
                          frequency=None, interval=None, feature_list=None, schedule_start=None, alert_config=None,
                          drift_threshold=None):
        r"""Create a new DataDriftDetector object in the Azure Machine Learning Workspace.

        Throws an exception if a DataDriftDetector for the same model_name and model_version already exists in the
        workspace.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :param services: Optional, list of AzureML webservices to run DataDriftDetector schedule
        :type services: builtin.list[str]
        :param compute_target_name: Optional, AzureML ComputeTarget name; DataDriftDetector will create one if none
                                    specified
        :type compute_target_name: str
        :param frequency: Optional, how often the pipeline is run. Supports "Day", "Week" or "Month"
        :type frequency: str
        :param interval: Optional, how often the pipeline runs based on frequency. i.e. If frequency = "Day" and \
                         interval = 2, the pipeline will run every other day
        :type interval: int
        :param feature_list: Optional, whitelisted features to run the datadrift detection on. DataDriftDetector jobs
                             will run on all features if no feature_list is specified.
        :type feature_list: builtin.list[str]
        :param schedule_start: Optional, start time of data drift schedule in UTC. Current time used if None specified
        :type schedule_start: datetime.datetime
        :param alert_config: Optional, configuration object for DataDriftDetector alerts
        :type alert_config: azureml.datadrift.AlertConfiguration
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on. Defaults to 0.2
        :type drift_threshold: float
        :return: A DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        model_name = ParameterValidator.validate_model_name(model_name)
        model_version = ParameterValidator.validate_model_version(model_version)
        services = ParameterValidator.validate_services(services)
        compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name, workspace)
        frequency = ParameterValidator.validate_frequency(frequency)
        interval = ParameterValidator.validate_interval(interval)
        feature_list = ParameterValidator.validate_feature_list(feature_list)
        schedule_start = ParameterValidator.validate_datetime(schedule_start)
        alert_config = ParameterValidator.validate_alert_configuration(alert_config)
        drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.create_from_model')
        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        _TelemetryLogger.log_event(DATADRIFT_CREATE_FROM_MODEL, **log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="datadriftdetector.create_from_model") as logger:

            dd_client = DataDriftClient(workspace.service_context)

            try:
                if list(dd_client.list(model_name, model_version, logger=logger)):
                    error_msg = "DataDriftDetector already exists for model_name: {}, model_version: {}. Please use " \
                                "DataDriftDetector.get() to retrieve the object".format(model_name, model_version)
                    logger.error(error_msg)
                    raise KeyError(error_msg)
            except HttpOperationError:
                # DataDriftDetector object doesn't exist for model_name and model_version, create one instead
                logger.info("Error checking DataDriftDetector object for model_name: {}, model_version: {}"
                            .format(model_name, model_version))
                raise

            if not compute_target_name:
                # Set to default workspace compute if it exists
                compute_target_name = DataDriftDetector._get_default_compute_target(workspace)

            if not drift_threshold:
                drift_threshold = DEFAULT_DRIFT_THRESHOLD

            # Write object to service
            dto = CreateDataDriftDto(frequency=frequency,
                                     schedule_start_time=schedule_start.replace(tzinfo=timezone.utc).isoformat()
                                     if schedule_start else None,
                                     interval=interval,
                                     alert_configuration=AlertConfiguration(
                                         email_addresses=alert_config.email_addresses)
                                     if alert_config else None,
                                     model_name=model_name,
                                     model_version=model_version,
                                     services=services,
                                     compute_target_name=compute_target_name,
                                     drift_threshold=drift_threshold,
                                     features=feature_list,
                                     type=DATADRIFT_TYPE_MODEL)
            client_dto = dd_client.create(dto, logger)
            DataDriftDetector._validate_client_dto(client_dto, logger)

            dd = DataDriftDetector(..., ..., ...)
            dd._initialize(workspace, client_dto)
            return dd

    @staticmethod
    def create_from_datasets(workspace, name, baseline_dataset, target_dataset, compute_target_name=None,
                             frequency=None, feature_list=None, alert_config=None, drift_threshold=None, latency=None):
        """Create a new DataDriftDetector object from a baseline dataset and a time series target dataset.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param name: Unique name of the DataDriftDetector object
        :type name: str
        :param baseline_dataset: Dataset to compare the target dataset against
        :type baseline_dataset: azureml.core.Dataset
        :param target_dataset: Dataset to run either adhoc or scheduled DataDrift jobs for. Must be Time Series
        :type target_dataset: azureml.core.Dataset
        :param compute_target_name: Optional, AzureML ComputeTarget name; DataDriftDetector will create one if none
                                    specified
        :type compute_target_name: str
        :param frequency: Optional, how often the pipeline is run. Supports "Day", "Week" or "Month"
        :type frequency: str
        :param feature_list: Optional, whitelisted features to run the datadrift detection on. DataDriftDetector jobs
                             will run on all features if no feature_list is specified.
        :type feature_list: builtin.list[str]
        :param alert_config: Optional, configuration object for DataDriftDetector alerts
        :type alert_config: azureml.datadrift.AlertConfiguration
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on. Defaults to 0.2
        :type drift_threshold: float
        :param latency: Delay (hours) for data to appear in dataset
        :type latency: int
        :return: A DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        name = ParameterValidator.validate_name(name)
        baseline_dataset = ParameterValidator.validate_dataset(baseline_dataset)
        target_dataset = ParameterValidator.validate_timeseries_dataset(target_dataset)
        frequency = ParameterValidator.validate_frequency(frequency, dataset_based=True)
        feature_list = ParameterValidator.validate_feature_list(feature_list)
        drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)
        compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name, workspace)
        alert_config = ParameterValidator.validate_alert_configuration(alert_config)
        latency = ParameterValidator.validate_latency(latency)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.create_from_datasets')
        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'baseline_dataset': baseline_dataset.id, 'target_dataset': target_dataset.id,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        _TelemetryLogger.log_event(DATADRIFT_CREATE_FROM_DATASET, **log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="datadriftdetector.create_from_datasets") as logger:

            dd_client = DataDriftClient(workspace.service_context)

            try:
                temp_dd = DataDriftDetector._get_datadrift_by_name(workspace, name)
                if temp_dd:
                    msg = "DataDriftDetector with name {} already exists. Please use get_by_name() to " \
                          "retrieve it".format(name)
                    logger.error(msg)
                    raise KeyError(msg)
            except HttpOperationError or KeyError:
                # DataDriftDetector object doesn't exist with specified name, creating...
                pass

            if not compute_target_name:
                # Set to default workspace compute if it exists
                compute_target_name = DataDriftDetector._get_default_compute_target(workspace)

            if not drift_threshold:
                drift_threshold = DEFAULT_DRIFT_THRESHOLD

            # Ensure that datasets are saved to the workspace
            baseline_dataset._ensure_saved(workspace)
            target_dataset._ensure_saved(workspace)

            # Write object to service
            dto = CreateDataDriftDto(frequency=frequency,
                                     schedule_start_time=None,
                                     interval=1,
                                     alert_configuration=AlertConfiguration(
                                         email_addresses=alert_config.email_addresses)
                                     if alert_config else None,
                                     type=DATADRIFT_TYPE_DATASET,
                                     compute_target_name=compute_target_name,
                                     drift_threshold=drift_threshold,
                                     base_dataset_id=baseline_dataset.id,
                                     target_dataset_id=target_dataset.id,
                                     features=feature_list,
                                     job_latency=latency,
                                     name=name)
            client_dto = dd_client.create(dto, logger)
            DataDriftDetector._validate_client_dto(client_dto, logger)

            dd = DataDriftDetector(..., ..., ...)
            dd._initialize(workspace, client_dto)
            return dd

    @staticmethod
    def get(workspace, model_name, model_version):
        """Retrieve a unique DataDriftDetector object for a given workspace, model_name, model_version and list of services.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :return: DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        model_name = ParameterValidator.validate_model_name(model_name)
        model_version = ParameterValidator.validate_model_version(model_version)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.get')
        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}
        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        _TelemetryLogger.log_event(DATADRIFT_GET, **log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="get") as logger:
            logger.info("Getting DataDriftDetector object for: {} {} {}".format(workspace, model_name, model_version))
            return DataDriftDetector(workspace, model_name, model_version)

    @staticmethod
    def get_by_name(workspace, name):
        """Retrieve a unique DataDriftDetector object for a given workspace and name.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param name: Unique name of the DataDriftDetector object
        :type name: str
        :return: DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        name = ParameterValidator.validate_name(name)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.get_by_name')
        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'name': name, 'subscription_id': workspace.subscription_id,
                       'workspace_location': workspace.location}
        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        _TelemetryLogger.log_event(DATADRIFT_GET_BY_NAME, **log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="get_by_name") as logger:
            logger.info("Getting DataDriftDetector object with name: {} in workspace: {}".format(name, workspace))
            try:
                client_dto = DataDriftDetector._get_datadrift_by_name(workspace, name, logger)
            except ServiceException as e:
                error_msg = "Could not find DataDriftDetector with name: {}".format(name)
                logger.error(error_msg, e)
                raise KeyError(error_msg, e)
            dd = DataDriftDetector(..., ..., ...)
            dd._initialize(workspace, client_dto)

            return dd

    @staticmethod
    def list(workspace, model_name=None, model_version=None, baseline_dataset=None, target_dataset=None):
        """Get a list of DataDriftDetector objects given a workspace.

        For Model Based DataDriftDetectors, pass in `model_name` and/or `model_version`, for Dataset Based
        DataDriftDetectors, pass in `baseline_dataset` and/or `target_dataset`. NOTE: Model Based optional parameters
        cannot be mixed with Dataset Based optional parameters. Passing in only workspace will return all
        DataDriftDetector objects, both Model Based and Dataset Based, from the workspace.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Optional, name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Optional, version of model
        :type model_version: int
        :param baseline_dataset: Dataset to compare the target dataset against
        :type baseline_dataset: azureml.core.Dataset
        :param target_dataset: Dataset to run either adhoc or scheduled DataDrift jobs for. Must be Time Series
        :type target_dataset: azureml.core.Dataset
        :return: List of DataDriftDetector objects
        :rtype: :class:list(azureml.datadrift.DataDriftDetector)
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        if model_name is not None:
            model_name = ParameterValidator.validate_model_name(model_name)
        if model_version is not None:
            model_version = ParameterValidator.validate_model_version(model_version)

        baseline_dataset = ParameterValidator.validate_dataset(baseline_dataset, none_ok=True)
        target_dataset = ParameterValidator.validate_dataset(target_dataset, none_ok=True)

        # Ensure Model Based and Dataset Based params are not arguments
        if model_name or model_version:
            if baseline_dataset or target_dataset:
                raise TypeError("Cannot have both Model Based and Dataset Based arguments")

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.list')
        log_context = {'workspace_name': workspace.name, 'workspace_id': workspace._workspace_id,
                       'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}
        if baseline_dataset:
            log_context['baseline_dataset'] = baseline_dataset.id
        if target_dataset:
            log_context['target_dataset'] = target_dataset.id
        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        _TelemetryLogger.log_event(DATADRIFT_LIST, **log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="list") as logger:
            dto_list = DataDriftDetector._get_datadrift_list(workspace, model_name=model_name,
                                                             model_version=model_version,
                                                             baseline_dataset=baseline_dataset,
                                                             target_dataset=target_dataset, logger=logger)
            dd_list = []
            for client_dto in dto_list:
                dd = DataDriftDetector(..., ..., ...)
                dd._initialize(workspace, client_dto)
                dd_list.append(dd)
            return dd_list

    @staticmethod
    def _get_default_compute_target(workspace):
        """If the Workspace default compute target exists retrieve its name, or return the default compute target name.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :return: Compute target name
        :rtype: str
        """
        return workspace.get_default_compute_target('CPU').name \
            if workspace.get_default_compute_target('CPU') \
            else DEFAULT_COMPUTE_TARGET_NAME

    @staticmethod
    def _get_datadrift_list(workspace, model_name=None, model_version=None, baseline_dataset=None, target_dataset=None,
                            services=None, logger=None, client=None):
        """Get list of DataDriftDetector objects from service.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Optional, name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Optional, version of model
        :type model_version: int
        :param services: Optional, names of webservices
        :type services: builtin.list[str]
        :param baseline_dataset: Dataset to compare the target dataset against
        :type baseline_dataset: azureml.core.Dataset
        :param target_dataset: Dataset to run either adhoc or scheduled DataDrift jobs for. Must be Time Series
        :type target_dataset: azureml.core.Dataset
        :param logger: Activity logger for service call
        :type logger: datetime.datetime
        :param client: DataDriftDetector service client
        :type client: azureml.datadrift._restclient.DataDriftClient
        :return: List of DataDriftDetector objects
        :rtype: list(azureml.datadrift._restclient.models.DataDriftDto)
        """
        dd_client = client if client else DataDriftClient(workspace.service_context)

        baseline_dataset_id = baseline_dataset.id if baseline_dataset else None
        target_dataset_id = target_dataset.id if target_dataset else None

        return list(dd_client.list(model_name=model_name, model_version=model_version, services=services,
                                   base_dataset_id=baseline_dataset_id, target_dataset_id=target_dataset_id,
                                   logger=logger))

    @staticmethod
    def _get_datadrift_by_name(workspace, name, logger=None, client=None):
        """Get list of DataDriftDetector objects from service.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param name: Unique name of the DataDriftDetector object
        :param logger: Activity logger for service call
        :type logger: datetime.datetime
        :param client: DataDriftDetector service client
        :type client: azureml.datadrift._restclient.DataDriftClient
        :return: List of DataDriftDetector objects
        :rtype: list(azureml.datadrift._restclient.models.DataDriftDto)
        """
        dd_client = client if client else DataDriftClient(workspace.service_context)

        return dd_client.get_by_name(name=name, logger=logger)

    @staticmethod
    def _create_aml_compute(workspace, name):
        """Create an aml compute using name.

        Create a new one.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param name: the name of aml compute target
        :type name: str
        :return: Azure ML Compute target
        :rtype: azureml.core.compute.compute.AmlCompute
        """
        log_context = {'workspace_name': workspace.name, 'subscription_id': workspace.subscription_id,
                       'workspace_location': workspace.location}
        # TODO: De-provision compute if it's not run
        module_logger.info("creating new compute target: {}".format(name), extra={'properties': log_context})

        if name == Workspace.DEFAULT_CPU_CLUSTER_NAME:
            # Use AzureML default aml compute config
            aml_compute = AmlCompute.create(workspace,
                                            Workspace.DEFAULT_CPU_CLUSTER_NAME,
                                            Workspace.DEFAULT_CPU_CLUSTER_CONFIGURATION)
        else:
            provisioning_config = AmlCompute.provisioning_configuration(
                vm_size=DEFAULT_VM_SIZE,
                max_nodes=DEFAULT_VM_MAX_NODES
            )
            aml_compute = AmlCompute.create(workspace, name, provisioning_config)

        aml_compute.wait_for_completion(show_output=True)
        return aml_compute

    def run(self, target_date, services=None, compute_target_name=None, create_compute_target=False,
            feature_list=None, drift_threshold=None):
        """Run an ad-hoc data drift detection run on a model for a specified time window.

        :param services: Optional, If Model Based, list of webservices to run DataDrift job on.
                         Not needed for Dataset Based DataDriftDetectors.
        :type services: builtin.list[str]
        :param target_date:  Target date of scoring data in UTC
        :type target_date: datetime.datetime
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param create_compute_target: Optional, whether the DataDriftDetector API should automatically create an AML
                                      compute target. Default to False.
        :type create_compute_target: bool
        :param feature_list: Optional, whitelisted features to run the datadrift detection on
        :type feature_list: builtin.list[str]
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on
        :type drift_threshold: float
        :return: DataDriftDetector run
        :rtype: azureml.core.run.Run
        """
        target_date = ParameterValidator.validate_datetime(target_date)
        if services and self.drift_type == DATADRIFT_TYPE_DATASET:
            raise TypeError("This DataDriftDetector is {}, please remove the services parameter".format(
                self.drift_type))
        services = ParameterValidator.validate_services(services, none_ok=True)
        compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name, self.workspace,
                                                                              not_exist_ok=create_compute_target)
        feature_list = ParameterValidator.validate_feature_list(feature_list)
        drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)
        _TelemetryLogger.log_event(DATADRIFT_RUN, **self._logger.context)
        with _TelemetryLogger.log_activity(self._logger, activity_name="run") as logger:
            if not compute_target_name:
                # Fallback to object's compute target
                compute_target_name = self.compute_target_name

            if not drift_threshold:
                # Fallback to object's drift threshold
                drift_threshold = self.drift_threshold

            if not feature_list:
                # Fallback to object's feature list
                feature_list = self.feature_list

            if not services:
                # Fallback to object's feature list
                feature_list = self.services

            self._get_compute_target(compute_target_name=compute_target_name,
                                     create_compute_target=create_compute_target, logger=logger)

            dto = CreateDataDriftRunDto(services=services,
                                        compute_target_name=compute_target_name,
                                        start_time=target_date.replace(tzinfo=timezone.utc).isoformat(),
                                        features=feature_list,
                                        drift_threshold=drift_threshold,
                                        run_type=RUN_TYPE_ADHOC)
            run_dto = self._client.run(self._id, dto, logger, api_version=PUBLICPREVIEW)

            exp = Experiment(self.workspace, run_dto.data_drift_id)
            run = Run(experiment=exp, run_id=run_dto.execution_run_id)
            return run

    def backfill(self, start_date, end_date, compute_target_name=None, create_compute_target=False):
        """Run a backfill job over a given specified start_date and end_date.

        *NOTE*: Backfill is only supported on Dataset Based DataDriftDetector objects.

        :param start_date:  Date to start the backfill job on
        :type start_date: datetime.datetime
        :param end_date:  End date of backfill job, inclusive
        :type end_date: datetime.datetime
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param create_compute_target: Optional, whether the DataDriftDetector API should automatically create an AML
                                      compute target. Default to False.
        :type create_compute_target: bool
        :return: DataDriftDetector run
        :rtype: azureml.core.run.Run
        """
        start_date, end_date = ParameterValidator.validate_start_date_end_date(start_date, end_date, self.frequency)

        if self.drift_type == DATADRIFT_TYPE_MODEL:
            raise TypeError("Cannot run backfill on Model Based DataDriftDetector, please use run().")
        compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name, self.workspace,
                                                                              not_exist_ok=create_compute_target)
        _TelemetryLogger.log_event(DATADRIFT_BACKFILL, **self._logger.context)
        with _TelemetryLogger.log_activity(self._logger, activity_name="backfill") as logger:
            if not compute_target_name:
                # Fallback to object's compute target
                compute_target_name = self.compute_target_name

            self._get_compute_target(compute_target_name=compute_target_name,
                                     create_compute_target=create_compute_target, logger=logger)

            dto = CreateDataDriftRunDto(compute_target_name=compute_target_name,
                                        start_time=start_date.replace(tzinfo=timezone.utc).isoformat(),
                                        end_time=end_date.replace(tzinfo=timezone.utc).isoformat(),
                                        run_type=RUN_TYPE_BACKFILL)

            run_dto = self._client.run(self._id, dto, logger, api_version=PUBLICPREVIEW)

            exp = Experiment(self.workspace, run_dto.data_drift_id)
            run = Run(experiment=exp, run_id=run_dto.execution_run_id)
            return run

    def enable_schedule(self, create_compute_target=False):
        """Create a schedule to run  a datadrift job for a specified model and webservice.

        :param create_compute_target: Optional, whether the DataDriftDetector API should automatically create an AML
                                      compute target. Default to False.
        :type create_compute_target: bool
        """
        _TelemetryLogger.log_event(DATADRIFT_ENABLE_SCHEDULE, **self._logger.context)
        with _TelemetryLogger.log_activity(self._logger, activity_name="enable_schedule") as logger:
            # TODO: Add check for baseline dataset property being set
            compute_target = self._get_compute_target(self.compute_target_name, create_compute_target, logger)
            compute_target_type = compute_target.type
            if compute_target_type != COMPUTE_TARGET_TYPE_AML:
                raise AttributeError(
                    "Compute target {} must be of type {} while it is {}".format(
                        self.compute_target_name,
                        COMPUTE_TARGET_TYPE_AML,
                        compute_target_type))

            try:
                self._state = ScheduleState.Enabled.name
                dto = self._update_remote(logger)
                self._schedule_id = dto.schedule_id
                self._schedule_start = dto.schedule_start_time if dto.schedule_start_time else None
                self._state = dto.state

                schedule = Schedule.get(self.workspace, self._schedule_id)
                schedule._wait_for_provisioning(3600)

            except HttpOperationError or SystemError:
                logger.exception("Unable to enable the schedule in workspace: {}".format(self.workspace))
                raise

    def disable_schedule(self):
        """Disable a schedule for a specified model and web service."""
        _TelemetryLogger.log_event(DATADRIFT_DISABLE_SCHEDULE, **self._logger.context)
        with _TelemetryLogger.log_activity(self._logger, activity_name="disable_schedule") as logger:
            try:
                self._state = ScheduleState.Disabled.name
                self._update_remote(logger)

                schedule = Schedule.get(self.workspace, self._schedule_id)
                schedule._wait_for_provisioning(3600)

            except HttpOperationError or SystemError:
                logger.exception(
                    "Unable to disable the schedule with ID: {} in workspace: {}".format(
                        self._schedule_id,
                        self.workspace))
                raise

    def get_output(self, start_time=None, end_time=datetime.combine(date.today(), datetime.min.time()), run_id=None):
        """Get a tuple of the drift results and metrics for a specific DataDriftDetector in over a given time window.

        .. remarks::
            Given there are three run types, adhoc run, scheduled run and backfill run. This attribute will be used
            to retrieve corresponding results in different ways:

            * To retrieve adhoc run results, there is only one way: run_id should be a valid guid run id.
            * To retrieve scheduled runs and backfill runs' results, there are two different ways: assign a valid guid
                run id to run_id, or assign specific start_time and/or end_time while keeping run_id as None;
            * If run_id and start_time/end_time are not None in the same invoking, parameter validation exception
                will be thrown.

            It's possible that there are multiple results for the same target date (target date means target dataset
            start date for dataset based drift, or scoring date for model based drift). Therefore it's necessary to
            identify and handle duplicated results. For dataset based drift, if results are for the same target date,
            then they are duplicated results. For model based drift, if results are for the same target date and about
            the same service, then they are deuplicated results. The get_output attribute will dedup these duplicated
            result by one rule: always pick up the latest generated results.

            The get_output attribute can be used to retrieve all outputs or partial outputs of scheduled runs in a
            specific time range between 'start_tzime' and 'end_time' (boundary included). User can also limited to
            results of an individual adhoc 'run_id'.

            * Principle for filtering is "overlapping": as long as there is an overlap between the actual result time
                (scoring date for model based drift, target dataset's [start date, end date] for dataset based drift)
                and the given [start_time, end_time], that result will be picked up.

            * Given there are multiple types of data drift instance, the result contents could be various.
                For example, for model based results, it will look like:

            .. code-block:: python

                # results : [{'drift_type': 'ModelBased' or 'DatasetBased', 'service_name': 'service1',
                #             'result':[{'has_drift': True, 'datetime': '2019-04-03', 'drift_threshold': 0.3,
                #                        'model_name': 'modelName', 'model_version': 2}]}]
                # metrics : [{'drift_type': 'ModelBased' or 'DatasetBased', 'service_name': 'service1',
                #             'metrics': [{'schema_version': '0.1', 'datetime': '2019-04-03',
                #                          'model_name': 'modelName', 'model_version': 2,
                #                          'dataset_metrics': [{'name': 'datadrift_coefficient', 'value': 0.3453}],
                #                          'column_metrics': [{'feature1': [{'name': 'datadrift_contribution',
                #                                                            'value': 288.0},
                #                                                           {'name': 'wasserstein_distance',
                #                                                            'value': 4.858040000000001},
                #                                                           {'name': 'energy_distance',
                #                                                            'value': 2.7204799576545313}]}]}]}]

                While for dataset based results, it will look like:

            .. code-block:: python

                # results : [{'drift_type': 'ModelBased' or 'DatasetBased',
                #             'result':[{'has_drift': True, 'drift_threshold': 0.3,
                #                        'start_date': '2019-04-03', 'end_date': '2019-04-04',
                #                        'base_dataset_id': '4ac144ef-c86d-4c81-b7e5-ea6bbcd2dc7d',
                #                        'target_dataset_id': '13445141-aaaa-bbbb-cccc-ea23542bcaf9'}]}]
                # metrics : [{'drift_type': 'ModelBased' or 'DatasetBased',
                #             'metrics': [{'schema_version': '0.1',
                #                          'start_date': '2019-04-03', 'end_date': '2019-04-04',
                #                          'baseline_dataset_id': '4ac144ef-c86d-4c81-b7e5-ea6bbcd2dc7d',
                #                          'target_dataset_id': '13445141-aaaa-bbbb-cccc-ea23542bcaf9'
                #                          'dataset_metrics': [{'name': 'datadrift_coefficient', 'value': 0.53459}],
                #                          'column_metrics': [{'feature1': [{'name': 'datadrift_contribution',
                #                                                            'value': 288.0},
                #                                                           {'name': 'wasserstein_distance',
                #                                                            'value': 4.858040000000001},
                #                                                           {'name': 'energy_distance',
                #                                                            'value': 2.7204799576545313}]}]}]}]

        :param start_time: Start time of results window in UTC, default is None, which means to pick up
                           the most recent 10th cycle's results.
        :type start_time: datetime.datetime, optional
        :param end_time: End time of results window in UTC, default is today.
        :type end_time: datetime.datetime, optional
        :param run_id: Optional, adhoc run id
        :type run_id: int
        :return: Tuple of a list of drift results, and a list of individual dataset and columnar metrics
        :rtype: tuple(:class:list(), :class:list())
        """
        if run_id and (start_time or end_time):
            raise ValueError("Either run_id or start_time/end_time should be None.")

        start_time = ParameterValidator.validate_datetime(start_time) if start_time \
            else self._start_time_of_the_most_recent_ten_cycles()
        end_time = ParameterValidator.validate_datetime(end_time) if end_time is not None else datetime.max
        run_id = ParameterValidator.validate_run_id(run_id) if run_id is not None else run_id
        _TelemetryLogger.log_event(DATADRIFT_GET_OUTPUT, **self._logger.context)
        return all_outputs(self._logger, Datastore.get_default(self.workspace),
                           self.workspace.get_details()["workspaceid"],
                           self.services, self.drift_type, self._id,
                           self._baseline_dataset_id, self._target_dataset_id,
                           self.model_name, self.model_version,
                           start_time, end_time, run_id)

    def update(self, services=..., compute_target_name=..., feature_list=..., schedule_start=..., alert_config=...,
               drift_threshold=...):
        r"""Update the schedule associated with the DataDriftDetector object.

        :param services: Optional, list of services to update
        :type services: builtin.list[str]
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param feature_list: Whitelisted features to run the datadrift detection on
        :type feature_list: builtin.list[str]
        :param schedule_start: Start time of data drift schedule in UTC
        :type schedule_start: datetime.datetime
        :param alert_config: Optional, configuration object for DataDriftDetector alerts
        :type alert_config: azureml.datadrift.AlertConfiguration
        :param drift_threshold: Threshold to enable DataDriftDetector alerts on
        :type drift_threshold: float
        :return: self
        :rtype: azureml.datadrift.DataDriftDetector
        """
        _TelemetryLogger.log_event(DATADRIFT_UPDATE, **self._logger.context)
        with _TelemetryLogger.log_activity(self._logger, activity_name="update") as logger:
            if services is not ...:
                services = ParameterValidator.validate_services(services)
                self._services = services
            if compute_target_name is not ...:
                self._compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name,
                                                                                            self.workspace)
                if not self._compute_target_name:
                    self._compute_target_name = self._get_default_compute_target(self.workspace)
            if feature_list is not ...:
                self._feature_list = ParameterValidator.validate_feature_list(feature_list)
            if schedule_start is not ...:
                self._schedule_start = ParameterValidator.validate_datetime(schedule_start)
            if alert_config is not ...:
                self._alert_config = ParameterValidator.validate_alert_configuration(alert_config)
            if drift_threshold is not ...:
                self._drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)
                if not self._drift_threshold:
                    self._drift_threshold = DEFAULT_DRIFT_THRESHOLD

            self._update_remote(logger)
            return self

    def _update_remote(self, logger):
        """Update the DataDriftDetector entry in the service database.

        :param logger: Activity logger for service call
        :type logger: datetime.datetime
        :return: DataDriftDetector data transfer object
        :rtype: logging.Logger
        """
        dto = UpdateDataDriftDto(compute_target_name=self._compute_target_name,
                                 alert_configuration=AlertConfiguration(
                                     email_addresses=self.alert_config.email_addresses)
                                 if self.alert_config else None,
                                 services=self._services,
                                 features=self._feature_list,
                                 drift_threshold=self._drift_threshold,
                                 state=self._state,)
        client_dto = self._client.update(self._id, dto, logger, api_version=PUBLICPREVIEW)
        DataDriftDetector._validate_client_dto(client_dto, logger)
        return client_dto

    def _get_compute_target(self, compute_target_name=None, create_compute_target=False, logger=None):
        """Get compute target.

        :type compute_target_name: str
        :param create_compute_target: if or not or create a aml compute target if not existing
        :type create_compute_target: boolean
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param logger: Optional, Datadrift logger
        :type logger: logging.LoggerAdapter
        :return: ComputeTarget
        :rtype: azureml.core.compute.ComputeTarget
        """
        # If any of the params below are None, this is a schedule run so default to the DataDriftDetector object's args
        if compute_target_name is None:
            compute_target_name = self.compute_target_name
        if logger is None:
            logger = self._logger

        try:
            compute_target = ComputeTarget(self.workspace, compute_target_name)
            return compute_target

        except ComputeTargetException as e:
            # get the aml compute target or create if it is not available and create_compute_target is True
            if create_compute_target:
                return self._create_aml_compute(self.workspace, compute_target_name)
            else:
                error_message = "compute target {} is not available." \
                                "Use create_compute_target=True to allow creation of a new compute target." \
                    .format(self.compute_target_name)
                logger.error(error_message)
                raise ComputeTargetException(error_message) from e

    @staticmethod
    # this attribute is also use in server side. (datadrift_run.py, _generate_script.py, msdcuration_run.py ...)
    # keep it to be compatible and call _get_metrics_path() for actual execution.
    def _get_metrics_path(model_name, model_version, service,
                          target_date=None, drift_type=DATADRIFT_TYPE_MODEL, datadrift_id=None):
        """Get the metric path for a given model version, instance target date and frequency of diff.

        :param model_name: Model name
        :type model_name: str
        :param model_version: Model version
        :type model_version: int
        :param service: Service name
        :type service: str
        :param target_date: Diff instance start time. If none datetime portion is ommitted.
        :type target_date: datetime.datetime
        :return: Relative paths to metric on datastore (model base and general)
        :rtype: str
        """
        return _get_metrics_path(model_name, model_version, service, target_date, drift_type, datadrift_id)

    def _start_time_of_the_most_recent_ten_cycles(self):
        start_date = date.today()

        if self.frequency == 'Day':
            start_date = start_date + timedelta(days=-10)
        elif self.frequency == 'Week':
            start_date = start_date + timedelta(weeks=-10)
        elif self.frequency == 'Month':
            start_date = start_date + relativedelta(months=-10)
        else:
            raise ValueError("Property frequency is not defined.")

        return datetime.combine(start_date, datetime.min.time())

    def show(self, start_time=None, end_time=datetime.combine(date.today(), datetime.min.time())):
        """Show data drift trend in given time range.

        By default it will show the most recent 10 cycles. For example, if frequency is day, then it will be the most
        recent 10 days, if frequency is week, then it will be the most recent 10 weeks.

        :param start_time: Optional, start of presenting time window in UTC, default is None, which means to pick up
                           the most recent 10th cycle's results.
        :type start_time: datetime.datetime
        :param end_time: Optional, end of presenting data time window in UTC, default is today.
        :type end_time: datetime.datetime
        :return: diction of all figures. Key is service_name
        :rtype: dict()
        """
        start_time_valid = ParameterValidator.validate_datetime(start_time) if start_time \
            else self._start_time_of_the_most_recent_ten_cycles()
        end_time_valid = ParameterValidator.validate_datetime(end_time)
        _TelemetryLogger.log_event(DATADRIFT_SHOW, **self._logger.context)
        return show(self._logger, Datastore.get_default(self.workspace),
                    self.workspace.get_details()["workspaceid"], self.workspace.name,
                    self.services, self.drift_type, self._id,
                    self._baseline_dataset_id, self._target_dataset_id,
                    self.model_name, self.model_version,
                    start_time_valid, end_time_valid)

    @staticmethod
    def _validate_client_dto(datadriftdto, logger):
        if datadriftdto is not None and datadriftdto.alert_configuration is not None and \
                datadriftdto.alert_configuration.email_addresses is not None \
                and len(datadriftdto.alert_configuration.email_addresses) > 0:
            # this means alert config is supposed to be set.
            if datadriftdto.alert_id is None:
                warnings.warn("Alert has not been setup for data-drift with model {} and version {}.\n".
                              format(datadriftdto.model_name, datadriftdto.model_version))
                if logger is not None:
                    logger.info("Alert has not been setup for data-drift with model {} and version {}.\n".
                                format(datadriftdto.model_name, datadriftdto.model_version))
