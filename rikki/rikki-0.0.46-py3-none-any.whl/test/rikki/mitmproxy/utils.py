from typing import Dict, Optional

from mitmproxy import http
from mitmproxy.test import tflow as flow_creator

from rikki.mitmproxy.model import Request, Response


def build_flow(
        request: Optional[Request] = None,
        response: Optional[Response] = None
) -> http.HTTPFlow:
    flow: http.HTTPFlow = flow_creator.tflow(resp=response is not None)

    if request:
        flow.request.host = request.host

        if request.headers:
            for header in request.headers.items():
                flow.request.headers[header[0]] = header[1]

        if request.params:
            for param in request.params.items():
                flow.request.query.set_all(param[0], [param[1]])

        if request.content:
            flow.request.content = request.content.encode("utf8")

    if response:
        if response.code:
            flow.response.status_code = response.code
        if response.headers:
            for header in response.headers.items():
                flow.response.headers.set_all(header[0], [header[1]])
        if response.content:
            flow.response.content = response.content.encode("utf8")

    return flow
