from unittest import TestCase

from mitmproxy import http

from rikki.mitmproxy.delegate_replace import InterceptAndReplace, ReplacementConfig
from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.util import contains_headers, contains_params
from test.rikki.mitmproxy.utils import build_flow


class TestReplacementDelegate(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.__filter_request = Request(
            host="example.com",
            content="example content",
            headers={"header1": "header1_value"},
            params={"param1": "param1_value"},
        )

        self.__replacement_request = Request(
            host="new_example.com",
            content="new content",
            headers={"new_header1": "new_header1_value"},
            params={"new_param1": "new_param1_value"},
        )

        self.__filter_response = Response(
            code=200,
            content="response_content",
            headers={"response_header_1": "response_header_1_value"}
        )

        self.__replacement_response = Response(
            code=300,
            content="new_response_content",
            headers={"new_response_header_1": "new_response_header_1_value"}
        )

    def test_request_replacement_by_request(self):
        flow: http.HTTPFlow = build_flow(
            request=self.__filter_request
        )

        config = ReplacementConfig(
            filter_request=self.__filter_request,
            replacement_request=self.__replacement_request
        )

        instance = InterceptAndReplace(config)

        instance.request(flow)

        assert flow.request.host == self.__replacement_request.host, "Host hasn't been replaced"
        assert flow.request.content == self.__replacement_request.content.encode("utf8"), "Content hasn't been replaced"
        assert contains_params(flow.request.query, self.__replacement_request.params), "Params hasn't been replaced"
        assert contains_headers(flow.request.headers,
                                self.__replacement_request.headers), "Headers hasn't been replaced"

    def test_response_replacement_by_request(self):
        flow: http.HTTPFlow = build_flow(
            request=self.__filter_request,
            response=self.__filter_response
        )

        config = ReplacementConfig(
            filter_request=self.__filter_request,
            replacement_response=self.__replacement_response
        )

        instance = InterceptAndReplace(config)

        instance.response(flow)

        assert flow.response.status_code == self.__replacement_response.code, "Response code hasn't been changed"
        assert contains_headers(flow.response.headers,
                                self.__replacement_response.headers), "Response headers hasn't been replaced"
        assert flow.response.content == self.__replacement_response.content.encode("utf8")

    def test_response_replacement_by_request_and_response(self):
        flow: http.HTTPFlow = build_flow(
            request=self.__filter_request,
            response=self.__filter_response
        )

        config = ReplacementConfig(
            filter_request=self.__filter_request,
            filter_response=self.__filter_response,
            replacement_response=self.__replacement_response
        )

        instance = InterceptAndReplace(config)
        instance.response(flow)

        assert flow.response.status_code == self.__replacement_response.code, "Response code hasn't been changed"
        assert contains_headers(flow.response.headers,
                                self.__replacement_response.headers), "Response headers hasn't been replaced"
        assert flow.response.content == self.__replacement_response.content.encode("utf8")

    def test_inclusive_replacement(self):
        flow: http.HTTPFlow = build_flow(
            request=self.__filter_request,
            response=self.__filter_response
        )

        replacement_request = Request(
            headers=self.__replacement_request.headers,
            params=self.__replacement_request.params
        )

        replacement_response = Response(
            headers=self.__replacement_response.headers
        )

        config = ReplacementConfig(
            filter_request=self.__filter_request,
            filter_response=self.__filter_response,
            replacement_request=replacement_request,
            replacement_response=replacement_response,
            inclusive=True
        )

        instance = InterceptAndReplace(config)
        instance.request(flow)
        instance.response(flow)

        assert len(flow.request.headers.items()) == len(config.replacement_request.headers.items())
        assert len(flow.request.query.items()) == len(config.replacement_request.params.items())
        assert len(flow.response.headers.items()) == len(config.replacement_response.headers.items())
