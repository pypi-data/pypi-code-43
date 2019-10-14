# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods used by automated machine learning."""
from typing import Union, Optional
from types import ModuleType
import importlib
import importlib.util
import importlib.abc
import json
import logging
import os
import numpy as np

from automl.client.core.common import utilities as common_utilities
from automl.client.core.common import constants
from automl.client.core.common.exceptions import AutoMLException
from automl.client.core.runtime.types import DataSingleColumnInputType
from .exceptions import ConfigException, ServiceException
from azureml.exceptions import ServiceException as AzureMLServiceException
from msrest.exceptions import HttpOperationError

from . import _constants_azureml
from ._azureautomlsettings import AzureAutoMLSettings


def friendly_http_exception(exception: Union[AzureMLServiceException, HttpOperationError], api_name: str) -> None:
    """
    Friendly exceptions for a http exceptions. This will pass through json formatted error responses.

    :param exception: exception raised from a network call.
    :param api_name: name of the API call made.
    :raise: AutoMLException
    """
    if hasattr(exception, 'error'):
        try:
            json.loads(exception.error)
            json.loads(exception.error.error)
            raise exception
        except Exception:
            pass
    try:
        status_code = exception.error.response.status_code

        # Raise bug with msrest team that response.status_code is always 500
        if status_code == 500:
            try:
                message = exception.message
                substr = 'Received '
                substr_idx = message.find(substr) + len(substr)
                status_code = int(message[substr_idx:substr_idx + 3])
            except Exception:
                pass
    except Exception:
        raise exception.with_traceback(exception.__traceback__)

    if status_code in _constants_azureml.HTTP_ERROR_MAP:
        http_error = _constants_azureml.HTTP_ERROR_MAP[status_code]
    else:
        http_error = _constants_azureml.HTTP_ERROR_MAP['default']
    if api_name in http_error:
        error_message = http_error[api_name]
    elif status_code == 400:
        # 400 bad request could be basically anything. Just pass the original exception message through
        error_message = exception.message
    else:
        error_message = http_error['default']
    raise AutoMLException(
        "{0} error raised. {1}".format(http_error['Name'], error_message), http_error['type']
    ).with_traceback(exception.__traceback__) from exception


def get_primary_metrics(task):
    """
    Get the primary metrics supported for a given task as a list.

    :param task: string "classification" or "regression".
    :return: A list of the primary metrics supported for the task.
    """
    return common_utilities.get_primary_metrics(task)


def _get_package_version():
    """
    Get the package version string.

    :return: The version string.
    """
    from . import __version__
    return __version__


def _load_user_script(script_path: str, logger: logging.Logger, calling_in_client_runtime: bool = True) -> ModuleType:
    #  Load user script to get access to GetData function
    logger.info('Loading data using user script.')

    module_name, module_ext = os.path.splitext(os.path.basename(script_path))
    if module_ext != '.py':
        raise ConfigException('The provided user script was not a Python file.')
    spec = importlib.util.spec_from_file_location('get_data', script_path)
    if spec is None:
        if calling_in_client_runtime:
            raise ConfigException('The provided user script path does not exist.')
        else:
            raise ServiceException('The provided user script path does not exist.')

    module_obj = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ConfigException(
            'The provided user script is a namespace package, which is not supported.')

    # exec_module exists on 3.4+, but it's marked optional so we have to assert
    assert isinstance(spec.loader, importlib.abc.Loader)
    assert spec.loader.exec_module is not None
    try:
        spec.loader.exec_module(module_obj)
    except FileNotFoundError:
        if calling_in_client_runtime:
            raise ConfigException('The provided user script path does not exist.')
        else:
            raise ServiceException('The provided user script path does not exist.')

    if not hasattr(module_obj, 'get_data'):
        raise ConfigException('The provided user script does not implement get_data().')

    return module_obj


def _check_if_y_label_has_single_frequency_class(automl_settings: AzureAutoMLSettings,
                                                 y: DataSingleColumnInputType,
                                                 logger: Optional[logging.Logger] = None) -> bool:
    """Check for classification tasks, if there is some label with only occurrence."""
    if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
        unique_classes_set, value_frequency_set = np.unique(y, return_counts=True)
        for class_value, frequency in zip(unique_classes_set, value_frequency_set):
            # In classification case if the there is label which has just one instance.
            # then we should auto-blacklist some pipelines
            if frequency == 1:
                if logger is not None:
                    logger.warning('Found class a with single occurrence. Some pipelines maybe blacklisted')
                return True

    return False


def _is_gpu() -> bool:
    is_gpu = False
    try:
        import torch
        is_gpu = torch.cuda.is_available()
    except ImportError:
        pass
    return is_gpu
