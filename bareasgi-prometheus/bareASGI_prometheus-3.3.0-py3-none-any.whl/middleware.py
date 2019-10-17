"""Prometheus middleware"""

from typing import Optional, Type

from baretypes import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpRequestCallback,
    HttpResponse
)

from .metrics import HttpRequestMetric, PrometheusHttpRequestMetric
from .monitor import monitor

class PrometheusMiddleware:
    """Prometheus Middleware"""

    def __init__(
            self,
            metric_type: Type[HttpRequestMetric] = None,
            name: Optional[str] = None
    ):
        self.metric_type = metric_type or PrometheusHttpRequestMetric
        self.name = name or 'bareASGI'

    async def __call__(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        with monitor(self.metric_type(self.name, scope, info, matches)) as metric:
            status, headers, content, pushes = await handler(scope, info, matches, content)
            metric.status = status
            return status, headers, content, pushes
