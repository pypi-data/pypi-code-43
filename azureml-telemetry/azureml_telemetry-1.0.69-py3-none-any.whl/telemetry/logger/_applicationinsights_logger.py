# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Represents a class used to log events and metrics to Application Insights.."""
from applicationinsights import TelemetryClient

from ._abstract_event_logger import AbstractEventLogger


class ApplicationInsightsEventLogger(AbstractEventLogger):
    """Represents a class used to log events and metrics to Application Insights.

    For more information see,
    `What is Application Insights? <https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview>`_.

    .. remarks::

        For more information see,
        `What is Application Insights? <https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview>`_.

    :param instrumentation_key: The Application Insights instrumentation key to use for sending telemetry.
    :param args: Optional arguments for formatting messages.
    :type args: list
    :param kwargs: Optional keyword arguments for adding additional information to messages.
    :type kwargs: dict
    """

    def __init__(self, instrumentation_key, *args, **kwargs):
        """
        Initialize a new instance of the ApplicationInsightsLogger.

        :param instrumentation_key: The Application Insights instrumentation key to use for sending telemetry.
        :type instrumentation_key: str
        :param args: Optional arguments for formatting messages.
        :type args: list
        :param kwargs: Optional keyword arguments for adding additional information to messages.
        :type kwargs: dict
        """
        self.telemetry_client = TelemetryClient(instrumentation_key=instrumentation_key)
        # flush telemetry every 30 seconds (assuming we don't hit max_queue_item_count first)
        self.telemetry_client.channel.sender.send_interval_in_milliseconds = 30 * 1000
        # flush telemetry if we have 10 or more telemetry items in our queue
        self.telemetry_client.channel.queue.max_queue_length = 10
        super(ApplicationInsightsEventLogger, self).__init__(*args, **kwargs)

    def log_event(self, telemetry_event):
        """
        Log an event to Application Insights.

        :param telemetry_event: The telemetry event to log.
        :type telemetry_event: Event
        :return: Event GUID.
        :rtype: str
        """
        self.telemetry_client.track_event(telemetry_event.name, self._fill_props_with_context(telemetry_event))
        return telemetry_event.required_fields.event_id

    def log_metric(self, telemetry_metric):
        """Log a metric to Application Insights.

        :param telemetry_metric: The telemetry metric to log.
        :type telemetry_metric: Metric
        :return: Metric GUID.
        :rtype: str
        """
        self.telemetry_client.track_metric(
            name=telemetry_metric.name,
            value=telemetry_metric.value,
            count=telemetry_metric.count,
            type=telemetry_metric.metric_type,
            max=telemetry_metric.metric_max,
            min=telemetry_metric.metric_min,
            std_dev=telemetry_metric.std_dev,
            properties=self._fill_props_with_context(telemetry_metric)
        )
        return telemetry_metric.required_fields.event_id

    def flush(self):
        """Flush the telemetry client."""
        self.telemetry_client.flush()
