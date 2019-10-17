"""An HTTP Request metric"""

from baretypes import (
    Scope,
    Info,
    RouteMatches
)

from jetblack_metrics import TimedMetric


class HttpRequestMetric(TimedMetric):
    """
    A metric which holds HTTP information.
    """

    def __init__(self, app_name: str, scope: Scope, info: Info, matches: RouteMatches) -> None:
        super().__init__()
        self.app_name = app_name
        self.scope = scope
        self.info = info
        self.matches = matches
        self.status = 500
