# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity-based loggers."""
from typing import Any, Dict, Iterator, List, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import copy
import contextlib
import logging
import platform
import re
import uuid

from automl.client.core.common import constants as constants
from automl.client.core.common import logging_utilities as logging_util

telemetry_enabled = False
try:
    from azureml.telemetry.contracts import (Event, RequiredFields, RequiredFieldKeys, StandardFields,
                                             StandardFieldKeys, ExtensionFields, ExtensionFieldKeys)

    telemetry_enabled = True
except ImportError:
    pass


class _AutoMLExtensionFieldKeys:
    ACTIVITY_STATUS_KEY = "ActivityStatus"
    AUTOML_CLIENT_KEY = "AutomlClient"
    AUTOML_CORE_SDK_VERSION_KEY = "AutomlCoreSdkVersion"
    AUTOML_SDK_VERSION_KEY = "AutomlSdkVersion"
    COMMON_CORE_VERSION_KEY = "CommonCoreVersion"
    COMPLETION_STATUS_KEY = "CompletionStatus"
    DURATION_IN_MILLISECONDS_KEY = "DurationMs"
    EXCEPTION_CLASS_KEY = "ExceptionClass"
    EXPERIMENT_ID_KEY = "ExperimentId"
    INNER_ERROR_CODE_KEY = "InnerErrorCode"
    IS_CRITICAL_KEY = "IsCritical"
    TRACEBACK_MESSAGE_KEY = "TracebackMessage"

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for AutoMlExtension fields."""
        current_keys = [
            _AutoMLExtensionFieldKeys.ACTIVITY_STATUS_KEY,
            _AutoMLExtensionFieldKeys.AUTOML_CLIENT_KEY,
            _AutoMLExtensionFieldKeys.AUTOML_CORE_SDK_VERSION_KEY,
            _AutoMLExtensionFieldKeys.AUTOML_SDK_VERSION_KEY,
            _AutoMLExtensionFieldKeys.COMMON_CORE_VERSION_KEY,
            _AutoMLExtensionFieldKeys.COMPLETION_STATUS_KEY,
            _AutoMLExtensionFieldKeys.DURATION_IN_MILLISECONDS_KEY,
            _AutoMLExtensionFieldKeys.EXCEPTION_CLASS_KEY,
            _AutoMLExtensionFieldKeys.EXPERIMENT_ID_KEY,
            _AutoMLExtensionFieldKeys.INNER_ERROR_CODE_KEY,
            _AutoMLExtensionFieldKeys.IS_CRITICAL_KEY,
            _AutoMLExtensionFieldKeys.TRACEBACK_MESSAGE_KEY
        ]

        current_keys.extend(ExtensionFieldKeys.keys())      # type: List[str]
        return current_keys


class ActivityLogger(logging.Logger, ABC):
    """Abstract base class for activity loggers."""

    def __init__(self, name: str = "ActivityLogger", *args: Any, **kwargs: Any):
        """Init a ActivityLogger class with default name.

        Keyword Arguments:
            :param name: logger instant name
            :type name: str

        """
        self.custom_dimensions = {'app_name': constants.DEFAULT_LOGGING_APP_NAME}   # type: Dict[str, Any]
        super().__init__(name, *args, **kwargs)
        if telemetry_enabled is False:
            return

    def _merge_kwarg_extra(self,
                           properties: Dict[str, Any],
                           **kwargs: Any) -> Tuple[Dict[str, Any], Any]:
        """Update and return the kwargs['extra'] as extra and the kwargs that pops extra key."""
        if "extra" in kwargs:
            properties = copy.deepcopy(self.custom_dimensions)
            extra = kwargs.pop("extra")
            if "properties" in extra:
                properties.update(extra['properties'])
            extra['properties'] = properties
        else:
            properties = self.custom_dimensions  # no need to update properties if no extra
            extra = {'properties': properties}
        return extra, kwargs

    def update_default_property(self,
                                key: str,
                                value: Any) -> None:
        """Update default property in the class.

        Arguments:
            :param key: The custom dimension key needs to be changed.
            :type key: str
            :param value: The value of the corresponding key.
            :type value: Any

        """
        self.update_default_properties({key: value})

    def update_default_properties(self,
                                  properties_dict: Dict[str, Any]) -> None:
        """Update default properties in the class.

        Arguments:
            :param properties_dict: The dict contains all the properties that need to be updated.
            :type properties_dict: dict

        """
        self.custom_dimensions.update(properties_dict)
        if telemetry_enabled is False:
            return

        self._update_schematized_fields()

    def set_custom_dimensions_on_log_config(self, log_config: logging_util.LogConfig) -> None:
        """
        Log activity with duration and status.

        :param log_config: LogConfig class.
        """
        log_config.set_custom_dimensions(self.custom_dimensions)

    def _update_schematized_fields(self):
        """
        Update schematized fields.

        Update required, standard, extension fields based on custom_dimensions.
        Since the schematized fields are shared with the C# SDK, we will be using
        camel case in the dimensions. Appropriate converters are used.
        """
        if telemetry_enabled is False:
            return

        cd = copy.deepcopy(self.custom_dimensions)
        for camel_key in RequiredFieldKeys.keys():
            snake_key = _camel_to_snake_case(camel_key)
            if snake_key in cd:
                self._required_fields[camel_key] = cd.pop(snake_key)

        for camel_key in StandardFieldKeys.keys():
            snake_key = _camel_to_snake_case(camel_key)
            if snake_key in cd:
                self._standard_fields[camel_key] = cd.pop(snake_key)

        for camel_key in _AutoMLExtensionFieldKeys.keys():
            snake_key = _camel_to_snake_case(camel_key)
            if snake_key in cd:
                self._extension_fields[camel_key] = cd.pop(snake_key)

        for snake_key in cd:
            self._extension_fields[_snake_to_camel_case(snake_key)] = cd[snake_key]

    @abstractmethod
    def _log_activity(self,
                      logger: Optional[logging.Logger],
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[Optional[Any]]:
        """
        Log activity - should be overridden by subclasses with a proper implementation.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        raise NotImplementedError

    @contextlib.contextmanager
    def log_activity(self,
                     logger: Optional[logging.Logger],
                     activity_name: str,
                     activity_type: Optional[str] = None,
                     custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[Optional[Any]]:
        """
        Log an activity using the given logger.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        return self._log_activity(logger, activity_name, activity_type, custom_dimensions)


class DummyActivityLogger(ActivityLogger):
    """Dummy activity logger."""

    def _log_activity(self,
                      logger: Optional[logging.Logger],
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[None]:
        """
        Do nothing.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        """
        yield


class TelemetryActivityLogger(ActivityLogger):
    """Telemetry activity logger."""

    def __init__(self, namespace=None,
                 filename=None,
                 verbosity=None,
                 custom_dimensions=None,
                 extra_handlers=None,
                 component_name=None,
                 required_fields=None,
                 standard_fields=None,
                 extension_fields=None,
                 *args, **kwargs):
        """
        Construct activity logger object.

        :param namespace: namespace
        :param filename: log file name
        :param verbosity: logger verbosity
        :param custom_dimensions: custom dimensions
        :param component_name: component name for telemetry state.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        """
        super().__init__("TelemetryActivityLogger", *args, **kwargs)
        self.namespace = namespace
        self.filename = filename
        self.verbosity = verbosity
        self.component_name = component_name
        self.custom_dimensions = {
            'app_name': constants.DEFAULT_LOGGING_APP_NAME,
            'automl_client': None,
            'automl_sdk_version': None,
            'child_run_id': None,
            'common_core_version': None,
            'compute_target': None,
            'experiment_id': None,
            'os_info': platform.platform(),
            'parent_run_id': None,
            'region': None,
            'service_url': None,
            'subscription_id': None,
            'task_type': None
        }

        if telemetry_enabled:
            self._required_fields = required_fields or RequiredFields()
            self._standard_fields = standard_fields or StandardFields()
            self._extension_fields = extension_fields or ExtensionFields()

        if custom_dimensions is not None:
            self.update_default_properties(custom_dimensions)

        self._logger = self._get_logger(extra_handlers)
        self._event_logger = logging_util.get_event_logger()
        if telemetry_enabled is False:
            return

        self._required_fields[RequiredFieldKeys.COMPONENT_NAME_KEY] = component_name
        self._standard_fields[StandardFieldKeys.CLIENT_OS_KEY] = platform.platform()
        if custom_dimensions is not None:
            self._standard_fields[StandardFieldKeys.ALGORITHM_TYPE_KEY] = custom_dimensions.get('task_type', None)
            self._standard_fields[StandardFieldKeys.COMPUTE_TYPE_KEY] = custom_dimensions.get('compute_target', None)

    def log(self,
            level: int,
            msg: str,
            *args: Any,
            **kwargs: Any) -> None:
        """Log message with custom dimensions.

        Arguments:
            :param level: Log level.
            :type level: int
            :param msg: logging message.
            :type msg: str

        """
        extra, kwargs = self._merge_kwarg_extra(self.custom_dimensions, **kwargs)
        self._logger.log(level, msg, extra=extra, *args, **kwargs)

    def debug(self,
              msg: str,
              *args: Any,
              **kwargs: Any) -> None:
        """Override logger debug.

        Arguments:
            :param msg: logging message.
            :type msg: str

        """
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self,
             msg: str,
             *args: Any,
             **kwargs: Any) -> None:
        """Override logger info.

        Arguments:
            :param msg: logging message.
            :type msg: str

        """
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self,
                msg: str,
                *args: Any,
                **kwargs: Any) -> None:
        """Override logger warning.

        Arguments:
            :param msg: logging message.
            :type msg: str

        """
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self,
              msg: str,
              *args: Any,
              **kwargs: Any) -> None:
        """Override logger error.

        Arguments:
            :param msg: logging message.
            :type msg: str

        """
        self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self,
                 msg: str,
                 *args: Any,
                 **kwargs: Any) -> None:
        """Override logger error.

        Arguments:
            :param msg: logging message.
            :type msg: str

        """
        self.log(logging.CRITICAL, msg, *args, **kwargs)

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        obj = {
            'namespace': self.namespace,
            'filename': self.filename,
            'verbosity': self.verbosity,
            'component_name': self.component_name,
            'custom_dimensions': self.custom_dimensions,
            '_logger': None,
            '_event_logger': None
        }

        if telemetry_enabled:
            obj.update({
                '_required_fields': self._required_fields,
                '_standard_fields': self._standard_fields,
                '_extension_fields': self._extension_fields
            })

        return obj

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.namespace = state['namespace']
        self.filename = state['filename']
        self.verbosity = state['verbosity']
        self.component_name = state['component_name']
        self.custom_dimensions = state['custom_dimensions']
        self._logger = self._get_logger()
        self._event_logger = logging_util.get_event_logger()
        if telemetry_enabled is False:
            return

        self._required_fields = state.get('_required_fields')
        self._standard_fields = state.get('_standard_fields')
        self._extension_fields = state.get('_extension_fields')

    def _get_logger(self, extra_handlers=None):
        return logging_util.get_logger(
            namespace=self.namespace,
            filename=self.filename,
            verbosity=self.verbosity,
            extra_handlers=extra_handlers,
            component_name=self.component_name)

    def _log_activity(self,
                      logger: Optional[logging.Logger],
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[None]:
        """
        Log activity with duration and status.

        :param logger: logger
        :param activity_name: activity name
        :param activity_type: activity type
        :param custom_dimensions: custom dimensions
        """
        activity_info = {'activity_id': str(uuid.uuid4()),
                         'activity_name': activity_name,
                         'activity_type': activity_type}  # type: Dict[str, Any]

        activity_info.update(self.custom_dimensions)
        activity_status = constants.Status.Started
        completion_status = constants.TelemetryConstants.SUCCESS

        start_time = datetime.utcnow()
        self._logger.info("ActivityStarted: {}".format(activity_name), extra={"properties": activity_info})
        self._log_status_event(activity_name=activity_name, activity_status=activity_status)

        activity_status = constants.Status.Completed
        try:
            yield
        except Exception:
            completion_status = constants.TelemetryConstants.FAILURE
            activity_status = constants.Status.Terminated
            raise
        finally:
            end_time = datetime.utcnow()
            duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
            activity_info["durationMs"] = duration_ms
            activity_info["completionStatus"] = completion_status

            self._logger.info("ActivityCompleted: Activity={}, HowEnded={}, Duration={}[ms]".
                              format(activity_name, completion_status, duration_ms),
                              extra={"properties": activity_info})
            self._log_status_event(activity_name, activity_status=activity_status,
                                   completion_status=completion_status, duration_milliseconds=duration_ms)

    def _log_status_event(self,
                          activity_name: str,
                          activity_status: str,
                          completion_status: Optional[str] = None,
                          duration_milliseconds: Optional[float] = None) -> None:
        if telemetry_enabled is False:
            return

        self._extension_fields[_AutoMLExtensionFieldKeys.ACTIVITY_STATUS_KEY] = activity_status
        if completion_status is not None:
            self._extension_fields[_AutoMLExtensionFieldKeys.COMPLETION_STATUS_KEY] = completion_status
        if duration_milliseconds is not None:
            self._extension_fields[_AutoMLExtensionFieldKeys.DURATION_IN_MILLISECONDS_KEY] = duration_milliseconds

        self._log_event(event_name=activity_name)

        self._extension_fields.pop(_AutoMLExtensionFieldKeys.ACTIVITY_STATUS_KEY, None)
        self._extension_fields.pop(_AutoMLExtensionFieldKeys.COMPLETION_STATUS_KEY, None)
        self._extension_fields.pop(_AutoMLExtensionFieldKeys.DURATION_IN_MILLISECONDS_KEY, None)

    def _log_error_event(self,
                         failure_reason: str,
                         error_code: str,
                         exception_class: str,
                         error_message: str,
                         traceback_message: str,
                         is_critical: bool = False) -> None:
        if telemetry_enabled is False:
            return

        self._extension_fields[_AutoMLExtensionFieldKeys.EXCEPTION_CLASS_KEY] = exception_class
        self._standard_fields[StandardFieldKeys.FAILURE_REASON_KEY] = failure_reason
        self._extension_fields[_AutoMLExtensionFieldKeys.INNER_ERROR_CODE_KEY] = error_code
        self._extension_fields[_AutoMLExtensionFieldKeys.IS_CRITICAL_KEY] = is_critical
        self._extension_fields[_AutoMLExtensionFieldKeys.TRACEBACK_MESSAGE_KEY] = traceback_message

        self._log_event(event_name=error_message)

        self._extension_fields.pop(_AutoMLExtensionFieldKeys.EXCEPTION_CLASS_KEY, None)
        self._standard_fields.pop(StandardFieldKeys.FAILURE_REASON_KEY, None)
        self._extension_fields.pop(_AutoMLExtensionFieldKeys.INNER_ERROR_CODE_KEY, None)
        self._extension_fields.pop(_AutoMLExtensionFieldKeys.IS_CRITICAL_KEY, None)
        self._extension_fields.pop(_AutoMLExtensionFieldKeys.TRACEBACK_MESSAGE_KEY, None)
        self._event_logger.flush()

    def _log_event(self, event_name: str) -> None:
        if telemetry_enabled is False:
            return

        event = Event(name=event_name,
                      required_fields=self._required_fields,
                      standard_fields=self._standard_fields,
                      extension_fields=self._extension_fields)

        self._event_logger.log_event(telemetry_event=event)


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def _camel_to_snake_case(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def _snake_to_camel_case(name):
    return ''.join(x.capitalize() or '_' for x in name.split('_'))
