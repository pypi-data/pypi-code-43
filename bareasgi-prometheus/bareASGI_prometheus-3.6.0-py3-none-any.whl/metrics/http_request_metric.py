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

    def __init__(
            self,
            host: str,
            app_name: str,
            scope: Scope,
            info: Info,
            matches: RouteMatches
    ) -> None:
        """Create an HTTP request metric
        
        :param host: The host
        :type host: str
        :param app_name: The name of the application
        :type app_name: str
        :param scope: The ASGI scope
        :type scope: Scope
        :param info: The application defined info
        :type info: Info
        :param matches: The route matches
        :type matches: RouteMatches
        """
        super().__init__()
        self.host = host
        self.app_name = app_name
        self.scope = scope
        self.info = info
        self.matches = matches
        self.status = 500
