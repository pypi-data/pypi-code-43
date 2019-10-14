# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Represents an in-memory event logger."""
import json

from ._abstract_event_logger import AbstractEventLogger


class InMemoryEventLogger(AbstractEventLogger):
    """Represents an in-memory event logger."""

    def __init__(self):
        """Initialize in memory event logger."""
        self.logs = []

    def log_event(self, telemetry_event):
        """Store the event into the dictionary.

        :param telemetry_event: the event to be logged
        :type telemetry_event: TelemetryObjectBase
        :return: Event GUID.
        :rtype: str
        """
        logged = self._fill_props_with_context(telemetry_event)
        print(logged)
        self.logs.append(logged)
        return telemetry_event.required_fields.event_id

    def log_metric(self, telemetry_metric):
        """Store the metric into the dictionary.

        :param telemetry_metric: the metric to be logged
        :type telemetry_metric: TelemetryObjectBase
        :return: Metric GUID.
        :rtype: str
        """
        logged = self._fill_props_with_context(telemetry_metric)
        print(logged)
        self.logs.append(logged)
        return telemetry_metric.required_fields.event_id

    def flush(self):
        """Flush the events."""
        json.dumps(self.logs)
