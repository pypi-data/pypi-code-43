# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for all loggers."""
from abc import ABC, abstractmethod

from azureml.telemetry.log_scope import LogScope as _LogScope


class AbstractEventLogger(ABC):
    """Abstract event logger class."""

    @abstractmethod
    def log_event(self, telemetry_event):
        """
        Log event.

        :param telemetry_event: the event to be logged
        :type telemetry_event: TelemetryObjectBase
        :return: Event GUID.
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def log_metric(self, telemetry_metric):
        """
        Log metric.

        :param telemetry_metric: the metric to be logged
        :type telemetry_metric: TelemetryObjectBase
        :return: Metric GUID.
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def flush(self):
        """Flush the telemetry client."""
        raise NotImplementedError()

    def _fill_props_with_context(self, telemetry_entry):
        """Fill telemetry props with context info.

        :param telemetry_entry: event or metric
        :type telemetry_entry: TelemetryObjectBase
        :return properties with context info
        :rtype: dict
        """
        props = telemetry_entry.get_all_properties()
        ctx = _LogScope.get_current()
        return props if ctx is None else ctx.get_merged_props(props)
