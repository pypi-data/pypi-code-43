from typing import Optional, List

from mitmproxy import http

from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.plugin import ProxyDelegate
from rikki.mitmproxy.util import filter


class AccumulateFilterConfig:

    def __init__(
            self,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
            in_send: Optional[str] = None,
            in_receive: Optional[str] = None
    ) -> None:
        super().__init__()
        self.request = request
        self.response = response
        self.in_send = in_send
        self.in_receive = in_receive


class Accumulate(ProxyDelegate):

    def __init__(self, filter_config: AccumulateFilterConfig):
        """
        This plugin will accumulate all flows filtered with the config. Be aware that flow will appear in results
        with delay in case when you specify response in filter config
        :param filter_config: request and response data, that will be used to filter requests
        """
        super().__init__()
        self.__config = filter_config
        self.accumulated_items: List[http.HTTPFlow] = []

    def request(self, flow: http.HTTPFlow):
        if self.__config.request and not self.__config.response:
            filtered_by_request = filter([flow], request=self.__config.request)
            if filtered_by_request and self.__config.in_send:
                if self.__check_everywhere(flow.request, self.__config.in_send):
                    self.accumulated_items.extend(filtered_by_request)
            else:
                self.accumulated_items.extend(filtered_by_request)
        if not self.__config.request and not self.__config.response:
            if self.__config.in_send and not self.__config.in_receive:
                if self.__check_everywhere(flow.request, self.__config.in_send):
                    self.accumulated_items.append(flow)

    def response(self, flow: http.HTTPFlow):
        if self.__config.response:
            filtered_flow = filter([flow], request=self.__config.request, response=self.__config.response)

            if filtered_flow and (self.__config.in_send or self.__config.in_receive):
                something_in_request = self.__check_everywhere(flow.request, self.__config.in_send)
                something_in_response = self.__check_everywhere(flow.request, self.__config.in_receive)
                if something_in_request or something_in_response:
                    self.accumulated_items.extend(filtered_flow)
            else:
                self.accumulated_items.extend(filtered_flow)

            if flow not in self.accumulated_items and \
                    self.__check_everywhere(data=flow.response, value=self.__config.in_receive):
                self.accumulated_items.append(flow)
        if not self.__config.request and not self.__config.response:
            if self.__config.in_send or self.__config.in_receive:
                something_in_request = self.__check_everywhere(flow.request, self.__config.in_send)
                something_in_response = self.__check_everywhere(flow.request, self.__config.in_receive)
                if something_in_request or something_in_response:
                    self.accumulated_items.append(flow)

    def clean_up(self):
        self.accumulated_items.clear()

    @staticmethod
    def __check_everywhere(data, value: Optional[str]) -> bool:
        if not value:
            return False
        if isinstance(data, http.HTTPRequest):
            request: http.HTTPRequest = data
            if request.content and value.lower().strip() in request.content.decode("utf8").lower().strip():
                return True
            if value.lower().strip() in request.pretty_url.lower().strip():
                return True
            if request.headers and value.lower().strip() in str(request.headers).lower().strip():
                return True
        if isinstance(data, http.HTTPResponse):
            response: http.HTTPResponse = data
            if response.content and value.lower().strip() in response.content.decode("utf8").lower().strip():
                return True
            if response.headers and value.lower().strip() in str(response.headers).lower().strip():
                return True
        return False
