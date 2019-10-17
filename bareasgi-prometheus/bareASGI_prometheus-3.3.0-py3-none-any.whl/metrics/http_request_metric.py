"""An HTTP Request metric"""

from baretypes import (
    Scope,
    Info,
    RouteMatches
)

from .timed_metric import TimedMetric


class HttpRequestMetric(TimedMetric):
    """
    A metric which holds HTTP information.
    """

    def __init__(self, name: str, scope: Scope, info: Info, matches: RouteMatches) -> None:
        super().__init__()
        self.name = name
        self.scope = scope
        self.info = info
        self.matches = matches
        self.status = 500
