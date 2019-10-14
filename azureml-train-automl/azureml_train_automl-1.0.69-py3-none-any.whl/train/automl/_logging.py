# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Auto ML common logging module."""
from typing import List, Optional, TYPE_CHECKING
import logging
import pkg_resources

from automl.client.core.common.activity_logger import TelemetryActivityLogger, _AutoMLExtensionFieldKeys
from azureml.telemetry import AML_INTERNAL_LOGGER_NAMESPACE, get_telemetry_log_handler
from azureml.telemetry.contracts import (RequiredFields,
                                         RequiredFieldKeys,
                                         StandardFields,
                                         StandardFieldKeys,
                                         ExtensionFields,
                                         ExtensionFieldKeys
                                         )
from .constants import ComputeTargets

TELEMETRY_AUTOML_COMPONENT_KEY = 'automl'


if TYPE_CHECKING:
    from ._azureautomlsettings import AzureAutoMLSettings


def get_logger(
    log_file_name: Optional[str] = None,
    verbosity: int = logging.DEBUG,
    automl_settings: 'Optional[AzureAutoMLSettings]' = None
) -> TelemetryActivityLogger:
    """
    Create the logger with telemetry hook.

    :param log_file_name: log file name
    :param verbosity: logging verbosity
    :param automl_settings: the AutoML settings object
    :return logger if log file name is provided otherwise null logger
    :rtype
    """
    telemetry_handler = get_telemetry_log_handler(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
    try:
        from automl.client.core.common import __version__ as CC_VERSION
        common_core_version = CC_VERSION    # type: Optional[str]
    except Exception:
        common_core_version = None

    azure_automl_sdk_version = pkg_resources.get_distribution("azureml-train-automl").version
    automl_core_sdk_version = pkg_resources.get_distribution("azureml-automl-core").version

    custom_dimensions = {
        "automl_client": "azureml",
        "common_core_version": common_core_version,
        "automl_sdk_version": azure_automl_sdk_version,
        "automl_core_sdk_version": automl_core_sdk_version
    }

    required_fields = RequiredFields()
    standard_fields = StandardFields()
    extension_fields = ExtensionFields()

    required_fields[RequiredFieldKeys.CLIENT_TYPE_KEY] = "sdk"
    required_fields[RequiredFieldKeys.CLIENT_VERSION_KEY] = azure_automl_sdk_version
    required_fields[RequiredFieldKeys.COMPONENT_NAME_KEY] = TELEMETRY_AUTOML_COMPONENT_KEY

    extension_fields[_AutoMLExtensionFieldKeys.COMMON_CORE_VERSION_KEY] = common_core_version
    extension_fields[_AutoMLExtensionFieldKeys.AUTOML_SDK_VERSION_KEY] = azure_automl_sdk_version
    extension_fields[_AutoMLExtensionFieldKeys.AUTOML_CORE_SDK_VERSION_KEY] = automl_core_sdk_version
    extension_fields[ExtensionFieldKeys.DISK_USED_KEY] = None

    if automl_settings is not None:
        if automl_settings.is_timeseries:
            task_type = "forecasting"
        else:
            task_type = automl_settings.task_type

        # Override compute target based on environment.
        compute_target = _InternalComputeTypes.identify_compute_type()
        if not compute_target:
            if automl_settings.compute_target == ComputeTargets.LOCAL:
                compute_target = _InternalComputeTypes.LOCAL
            elif automl_settings.compute_target == ComputeTargets.AMLCOMPUTE:
                compute_target = _InternalComputeTypes.AML_COMPUTE
            elif automl_settings.spark_service == 'adb':
                compute_target = _InternalComputeTypes.DATABRICKS
            else:
                compute_target = _InternalComputeTypes.REMOTE

        custom_dimensions.update(
            {
                "experiment_id": automl_settings.name,
                "task_type": task_type,
                "compute_target": compute_target,
                "subscription_id": automl_settings.subscription_id,
                "region": automl_settings.region
            }
        )

        standard_fields[StandardFieldKeys.ALGORITHM_TYPE_KEY] = task_type
        # Don't fill in the Compute Type as it is being overridden downstream by Execution service
        # ComputeTarget field is still logged in customDimensions that contains these values
        # standard_fields[StandardFieldKeys.COMPUTE_TYPE_KEY] = compute_target

        required_fields[RequiredFieldKeys.SUBSCRIPTION_ID_KEY] = automl_settings.subscription_id
        # Workspace name can have PII information. Therefore, not including it.
        # required_fields[RequiredFieldKeys.WORKSPACE_ID_KEY] = automl_settings.workspace_name

    logger = TelemetryActivityLogger(
        namespace=AML_INTERNAL_LOGGER_NAMESPACE,
        filename=log_file_name,
        verbosity=verbosity,
        extra_handlers=[telemetry_handler],
        custom_dimensions=custom_dimensions,
        required_fields=required_fields,
        standard_fields=standard_fields,
        extension_fields=extension_fields)
    return logger


class _InternalComputeTypes:
    """Class to represent all Compute types."""

    _AZURE_NOTEBOOK_VM_IDENTIFICATION_FILE_PATH = "/mnt/azmnt/.nbvm"
    _AZURE_SERVICE_ENV_VAR_KEY = "AZURE_SERVICE"

    AML_COMPUTE = "AmlCompute"
    ARCADIA = "Microsoft.ProjectArcadia"
    COSMOS = "Microsoft.SparkOnCosmos"
    DATABRICKS = "Microsoft.AzureDataBricks"
    HDINSIGHTS = "Microsoft.HDI"
    LOCAL = "local"
    NOTEBOOK_VM = "Microsoft.AzureNotebookVM"
    REMOTE = "remote"

    _AZURE_SERVICE_TO_COMPUTE_TYPE = {
        ARCADIA: ARCADIA,
        COSMOS: COSMOS,
        DATABRICKS: DATABRICKS,
        HDINSIGHTS: HDINSIGHTS
    }

    @classmethod
    def get(cls) -> List[str]:
        return [
            _InternalComputeTypes.ARCADIA,
            _InternalComputeTypes.COSMOS,
            _InternalComputeTypes.DATABRICKS,
            _InternalComputeTypes.HDINSIGHTS,
            _InternalComputeTypes.LOCAL,
            _InternalComputeTypes.NOTEBOOK_VM,
            _InternalComputeTypes.REMOTE
        ]

    @classmethod
    def identify_compute_type(cls, azure_service: Optional[str] = None) -> Optional[str]:
        """
        Identify compute target and return appropriate key from _Compute_Type

        For notebook VMs we need to check existence of a specific file.
        For Project Arcadia, HD Insights, Spark on Cosmos, Azure data bricks, we need to use
        AZURE_SERVICE environment variable which is set to specific values.
        These values are stored in _InternalComputeTypes.
        """
        import os
        if os.path.isfile(_InternalComputeTypes._AZURE_NOTEBOOK_VM_IDENTIFICATION_FILE_PATH):
            return _InternalComputeTypes.NOTEBOOK_VM

        azure_service = azure_service or os.environ.get(_InternalComputeTypes._AZURE_SERVICE_ENV_VAR_KEY)
        if azure_service is not None:
            return _InternalComputeTypes._AZURE_SERVICE_TO_COMPUTE_TYPE.get(azure_service, None)

        return None
