import threading

from typing import Optional, List

from mitmproxy import http

from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.plugin import ProxyDelegate
from rikki.mitmproxy.util import filter
import random


class DelayConfig:

    def __init__(
            self,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
            random: bool = False,
            delay: int = 0
    ) -> None:
        """
        :param request: request data for filter
        :param response: response data for filter
        :param delay:
        """
        self.request = request
        self.response = response
        self.delay = delay
        self.random = random


class Delay(ProxyDelegate):
    """
    This plugin will delay request processing based based on provided config.

    """

    def __init__(self, config: DelayConfig, recursive: bool = False):
        super().__init__(recursive=recursive)
        self.__config: DelayConfig = config

    def response(self, flow: http.HTTPFlow):
        filtered_flows = filter([flow], request=self.__config.request, response=self.__config.response)
        if not self.__config.random:
            self.__delay_flows(filtered_flows)
        else:
            if random.choice([True, False]):
                if filtered_flows:
                    self.__delay_flows(filtered_flows)
                else:
                    self.__delay_flows([flow])

    def __delay_flows(self, flows: List[http.HTTPFlow]):
        for flow in flows:
            flow.intercept()
        threading.Timer(self.__config.delay, self.__resume_flows, args=[flows]).start()

    @staticmethod
    def __resume_flows(flows: List[http.HTTPFlow]):
        for flow in flows:
            flow.resume()
