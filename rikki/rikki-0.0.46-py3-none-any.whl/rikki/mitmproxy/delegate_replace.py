from typing import Optional

from mitmproxy import http
from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.plugin import ProxyDelegate
from rikki.mitmproxy.util import filter as filter_flows, replace


class ReplacementConfig:

    def __init__(
            self,
            filter_request: Optional[Request] = None,
            filter_response: Optional[Response] = None,
            replacement_request: Optional[Request] = None,
            replacement_response: Optional[Response] = None,
            inclusive=False,
            wait_response=True
    ) -> None:
        """
        This config represents data to be used in @InterceptAndReplace class.
        :param filter_request:
        :param filter_response:
        :param replacement_request: Will be used to replace data in request if `request_filter` presented
        :param replacement_response: Will be used to replace data in response if `request_filter` or `response_filter`
        :param inclusive: when True will replace all data for Request/Response, if not will add the data to them and
        replace only conflicted properties
        presented.
        """
        super().__init__()
        self.filter_request: Optional[Request] = filter_request
        self.filter_response: Optional[Response] = filter_response
        self.replacement_request: Optional[Request] = replacement_request
        self.replacement_response: Optional[Response] = replacement_response
        self.inclusive = inclusive
        self.wait_response = wait_response


class InterceptAndReplace(ProxyDelegate):
    """
    This delegates responsible for intercepting and replacing of data in Request or Response
    """

    def __init__(self, config: ReplacementConfig, recursive: bool = True) -> None:
        """
        Initialise interception and replace plugin. The plugin will intercept requests or response
        :param request:
        :param response:
        """
        super().__init__(recursive=recursive)
        self.__config = config

    def request(self, flow: http.HTTPFlow):

        filtered = filter_flows([flow], request=self.__config.filter_request)
        for filtered_flow in filtered:
            if self.__config.replacement_request:
                self.__prepare_request(filtered_flow)
                replace(flow=filtered_flow, request=self.__config.replacement_request)
            if not self.__config.filter_response and not self.__config.wait_response:
                flow.response = http.HTTPResponse.make()

    def response(self, flow: http.HTTPFlow):
        filter_request = self.__config.filter_request

        if self.__config.replacement_request:
            filter_request = self.__config.replacement_request

        filtered = filter_flows([flow], request=filter_request,
                                response=self.__config.filter_response)
        for filtered_flow in filtered:
            if self.__config.replacement_response:
                self.__prepare_response(filtered_flow)
                replace(flow=filtered_flow, response=self.__config.replacement_response)

    def __prepare_request(self, flow: http.HTTPFlow):
        if self.__config.inclusive:
            if self.__config.replacement_request:
                if self.__config.replacement_request.headers:
                    flow.request.headers.clear()
                if self.__config.replacement_request.params:
                    flow.request.query.clear()

    def __prepare_response(self, flow: http.HTTPFlow):
        if self.__config.inclusive:
            if self.__config.replacement_response:
                if self.__config.replacement_response.headers:
                    flow.response.headers.clear()
