# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import logging
from collections import defaultdict, deque

from .events import RequestRecord
from .performance_metrics import RequestTrace, Trace
from .runner import MetricsEvent

LOGGER = logging.getLogger(__name__)

# Traces can be recorded out of a request, we keep the traces
# in the request recorder while waiting for the flush call. If there
# is no request for a while, the traces could pile up, so we limit their
# number and keep only the latest.
MAX_REQUEST_RECORDER_TRACES = 10000


class RequestRecorder:
    """Store observations related to a request."""

    def __init__(self):
        self.traces = deque(maxlen=MAX_REQUEST_RECORDER_TRACES)
        self.clear()

    def clear(self):
        """Clear all observations."""
        self.report = False
        self.payload_sections = set()
        self.observations = defaultdict(list)
        self.traces.clear()
        self.identity = None
        self.request_trace = None

    def trace(self, name=None):
        """Start a new trace from a request trace."""
        if self.request_trace is None:
            # There is not request at the moment, use a independant trace.
            return Trace(name, recorder=self)
        return self.request_trace.trace(name)

    def start_request(self, request, trace_request=False):
        """Start a request."""
        if trace_request:
            self.request_trace = RequestTrace(recorder=self)

    def end_request(self):
        """End the current request."""
        if self.request_trace is not None:
            self.request_trace.end()

    def record_trace(self, name, start_time, duration, at):
        """Record a performance metric."""
        if name is not None:
            LOGGER.debug("Performance metric %r: %.4f", name, duration)
            self.traces.append((name, at, None, duration))

    def observe(self, what, observation, payload_sections=None, report=True):
        """Record an observation."""
        if what == "sdk":
            name = observation[0]
            if name == "identify":
                self.identity = observation[2]
            elif self.identity and name == "track":
                identity = observation[3].get("user_identifiers")
                if identity and identity != self.identity:
                    LOGGER.warning(
                        "sqreen.identify and sqreen.track have been called "
                        "with different user_identifiers values"
                    )
        self.observations[what].append(observation)
        if payload_sections:
            self.payload_sections.update(payload_sections)
        if report:
            self.report = True

    def flush(self, request, response, payload_creator, queue, observation_queue):
        """Flush all observations."""
        if self.identity:
            # Tag unidentified track events with identity.
            for observation in self.observations["sdk"]:
                if observation[0] != "track":
                    continue
                track_options = observation[3]
                track_options.setdefault("user_identifiers", self.identity)

        self._put_metrics(queue, observation_queue)
        if self.report:
            payload = payload_creator.get_payload(
                request, response, self.payload_sections
            )
            # If request recorder must report the request, send also the
            # detailed observations.
            payload["observed"] = self.observations
            queue.put(RequestRecord(payload))
        self.clear()

    def _put_metrics(self, queue, observation_queue):
        # Send the performance metrics to observation queue for aggregation
        while self.traces:
            observation_queue.put(self.traces.popleft())
        # Aggregate observations if the request is not reported
        if not self.report:
            for observation in self.observations.get("observations", []):
                observation_queue.put(observation)
        if observation_queue.half_full():
            queue.put(MetricsEvent)
