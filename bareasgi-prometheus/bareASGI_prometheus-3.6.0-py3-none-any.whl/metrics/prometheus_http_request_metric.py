"""Monitors"""

from prometheus_client import Counter, Gauge, Histogram

from .http_request_metric import HttpRequestMetric

class PrometheusHttpRequestMetric(HttpRequestMetric):
    """
    Default context manager with request count, latency and in progress
    metrics.
    """

    REQUEST_COUNT = Counter(
        'http_request_count',
        "Number of requests received",
        ['host', 'app_name', 'method', 'path', 'status']
    )
    REQUEST_LATENCY = Histogram(
        'http_request_latency',
        "Elapsed time per request",
        ['host', 'app_name', 'method', 'path']
    )
    REQUEST_IN_PROGRESS = Gauge(
        'http_requests_in_progress',
        "Requests in progress",
        ['host', 'app_name', 'method', 'path']
    )

    def on_enter(self):
        super().on_enter()
        self.REQUEST_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.scope['method'],
            self.scope['path']
        ).inc()

    def on_exit(self) -> None:
        super().on_exit()
        self.REQUEST_COUNT.labels(
            self.host,
            self.app_name,
            self.scope['method'],
            self.scope['path'],
            self.status
        ).inc()
        self.REQUEST_LATENCY.labels(
            self.host,
            self.app_name,
            self.scope['method'],
            self.scope['path']
        ).observe(self.elapsed)
        self.REQUEST_IN_PROGRESS.labels(
            self.host,
            self.app_name,
            self.scope['method'],
            self.scope['path']
        ).dec()
