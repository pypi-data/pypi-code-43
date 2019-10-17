"""Helpers"""

from typing import Optional, Type

from bareasgi import Application

from .metrics import HttpRequestMetric
from .middleware import PrometheusMiddleware
from .view import prometheus_view

def add_prometheus_middleware(
        app: Application,
        metric_type: Optional[Type[HttpRequestMetric]] = None,
        metrics_path: Optional[str] = '/metrics'
) -> Application:
    """Adds prometheus middleware as the first middleware.

    :param app: The ASGI application
    :type app: Application
    :param request_monitor: An optional custom request monitor
    :type request_monitor: Optional[Type[BaseRequestMonitor]]
    :param metrics_path: An optional path for the metrics, defaults to None
    :type metrics_path: Optional[str], optional
    :return: The ASGI application
    :rtype: Application
    """
    prometheus_middleware = PrometheusMiddleware(metric_type)
    app.middlewares.insert(0, prometheus_middleware)

    if metrics_path:
        app.http_router.add({'GET'}, metrics_path, prometheus_view)

    return app
