# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import time
from datetime import datetime
from logging import getLogger
from operator import itemgetter

DEFAULT_PERF_LEVEL = 0  # 0: disabled; 1: enabled
DEFAULT_PERF_PERIOD = 60
DEFAULT_PERF_BASE = 2.0
DEFAULT_PERF_UNIT = 0.1  # ms
DEFAULT_PERF_PCT_BASE = 1.3
DEFAULT_PERF_PCT_UNIT = 1.0  # %

LOGGER = getLogger(__name__)


class PerformanceMetricsSettings:
    """ Performance metrics settings.
    """

    SETTINGS_FIELD_MAP = {
        'perf_level': 'level',
        'performance_metrics_period': 'period',
        'perf_base': 'base',
        'perf_unit': 'unit',
        'perf_pct_base': 'pct_base',
        'perf_pct_unit': 'pct_unit',
    }

    def __init__(self, level=DEFAULT_PERF_LEVEL,
                 period=DEFAULT_PERF_PERIOD,
                 base=DEFAULT_PERF_BASE,
                 unit=DEFAULT_PERF_UNIT,
                 pct_base=DEFAULT_PERF_PCT_BASE,
                 pct_unit=DEFAULT_PERF_PCT_UNIT):
        self.level = level
        self.period = period
        self.base = base
        self.unit = unit
        self.pct_base = pct_base
        self.pct_unit = pct_unit
        if self.enabled() and self.period == 0:
            LOGGER.warning("Setting performance period to default %d",
                           DEFAULT_PERF_PERIOD)
            self.period = DEFAULT_PERF_PERIOD

    @staticmethod
    def from_features(features):
        level = features.get('perf_level', DEFAULT_PERF_LEVEL)
        # old name, in Ruby not used for binned metrics:
        period = features.get('performance_metrics_period', DEFAULT_PERF_PERIOD)
        base = features.get('perf_base', DEFAULT_PERF_BASE)
        unit = features.get('perf_unit', DEFAULT_PERF_UNIT)
        pct_base = features.get('perf_pct_base', DEFAULT_PERF_PCT_BASE)
        pct_unit = features.get('perf_pct_unit', DEFAULT_PERF_PCT_UNIT)

        return PerformanceMetricsSettings(level=level, period=period,
                                          base=base, unit=unit,
                                          pct_base=pct_base, pct_unit=pct_unit)

    def as_features(self):
        return {k: getattr(self, v) for k, v in self.SETTINGS_FIELD_MAP.items()}

    def enabled(self):
        return self.level > 0


class Trace(object):
    """Trace execution time."""

    def __init__(self, name, recorder=None):
        self.name = name
        self.recorder = recorder
        # TODO use a monotonic clock but there is none on Python < 3.3.
        # Maybe work around this with a native extension.
        self.start_time = time.time()
        self.duration = None

    @property
    def duration_ms(self):
        """Convert the duration from seconds to milliseconds."""
        if self.duration is not None:
            return self.duration * 1000

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.end()
        except Exception:
            LOGGER.error("exception while ending a performance trace", exc_info=1)

    def end(self, at=None):
        """End a performance trace."""
        if self.duration is not None:
            LOGGER.debug("A trace was ended multiple times: %r", self)
            return
        end_time = time.time()
        self.duration = end_time - (self.start_time or end_time)
        if self.duration < 0:
            self.duration = 0
        if self.recorder is not None:
            if at is None:
                at = datetime.utcnow()
            self.recorder.record_trace(self.name, self.start_time, self.duration_ms, at)

    def __repr__(self):
        return "<{} name={!r} duration_ms={:.4f}>".format(
            self.__class__.__name__,
            self.name,
            self.duration_ms
        )


class RequestTrace(Trace):
    """Trace request execution time for performance monitoring.

    Sub traces can be created for monitoring rule execution
    time. When the request is terminated, the total rule execution
    time is computed. Beware, a sub trace cannot survive this trace,
    meaning when the end method is called, all sub-traces are ended too.
    """

    def __init__(self, recorder=None):
        self._traces = []
        self._timeline = []
        super(RequestTrace, self).__init__("req", recorder)

    def trace(self, name=None):
        """Start a sub-trace."""
        trace = Trace(name, recorder=self)
        # Keep an history of all traces to compute total sub trace duration
        self._timeline.append((1, (trace.start_time - self.start_time) * 1000.0))
        self._traces.append(trace)
        return trace

    def _compute_aggregated_duration(self):
        # This is a modified version of the algorithm used to solve the
        # "minimum number of platforms required" problem.
        # It computes the overall time spent in sub-traces taking into
        # account the overlapping traces.
        counter = 0
        start_t = 0
        end_t = 0
        duration = 0
        # The timeline should be already in order, make sure it is
        self._timeline.sort(key=itemgetter(1))
        for op, t in self._timeline:
            # Start interval
            if counter == 0 and op == 1:
                start_t = t
            # End interval
            elif counter == 1 and op == -1:
                duration += t - start_t
                end_t = t
            elif op == -1:
                end_t = t
            counter += op
        # If some traces are not finished, use the last interval end
        if counter > 0:
            duration += end_t - start_t
        return duration if duration >= 0 else 0

    @property
    def aggregated_duration_ms(self):
        """Return total time spent in sub-traces."""
        return self._compute_aggregated_duration()

    def record_trace(self, name, start_time, duration, at):
        """Aggregate values from sub-traces."""
        # End of a sub-trace, keep it in the timeline to compute aggregated
        # duration
        self._timeline.append((-1, (start_time - self.start_time) * 1000.0 + duration))
        if self.recorder is not None:
            self.recorder.record_trace(name, start_time, duration, at)

    def end(self, at=None):
        """End the trace and all sub traces."""
        # Automatically terminate sub traces to assure consistency
        if at is None:
            at = datetime.utcnow()
        for trace in self._traces:
            if trace.duration is None:
                trace.end(at=at)
        super(RequestTrace, self).end(at=at)
        if self.recorder is not None:
            aggregated_duration_ms = self._compute_aggregated_duration()
            self.recorder.record_trace("sq", None, aggregated_duration_ms, at)
            no_sq = self.duration_ms - aggregated_duration_ms
            if no_sq > 0:
                fraction = self.aggregated_duration_ms / no_sq
                self.recorder.record_trace("pct", None, 100.0 * fraction, at)
