from mitmproxy import http
from typing import List


class ProxyDelegate:

    def __init__(self, recursive: bool = True) -> None:
        """
        Delegate all jobs you need to be done by the proxy to instance of this class
        :param recursive: When True all previous requests will be feed into the delegate when it's added
        """
        super().__init__()
        self.recursive = recursive

    def request(self, flow: http.HTTPFlow): pass

    def response(self, flow: http.HTTPFlow): pass

    def shutdown(self): pass

    def clean_up(self): pass


class ProxyPlugin:
    """
    Base plugin implementation  for mitmproxy
    """

    def __init__(self):
        self._requests: List[http.HTTPFlow] = []
        self._delegates: List[ProxyDelegate] = []
        self.proxy = None

    def add_delegate(self, delegate: ProxyDelegate):
        self._delegates.append(delegate)
        if delegate.recursive:
            for flow in self._requests:
                delegate.request(flow)
                if flow.response:
                    delegate.response(flow)

    def load(self, loader):
        pass

    def configure(self, updated):
        pass

    def request(self, flow: http.HTTPFlow):
        self._requests.append(flow)
        for delegate in self._delegates:
            delegate.request(flow)

    def response(self, flow: http.HTTPFlow):
        for delegate in self._delegates:
            delegate.response(flow)

    def reset(self):
        self._requests = []
        self._delegates = []

    def shutdown(self):
        for delegate in self._delegates:
            delegate.shutdown()
        if self.proxy:
            self.proxy.shutdown()

    def clean_up(self):
        self._requests.clear()
        for delegate in self._delegates:
            delegate.clean_up()
