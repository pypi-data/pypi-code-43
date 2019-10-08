from unittest import TestCase

from rikki.mitmproxy.delegate_accumulate import AccumulateFilterConfig, Accumulate
from rikki.mitmproxy.model import Request, Response
from rikki.mitmproxy.util import filter
from test.rikki.mitmproxy.utils import build_flow


class TestAccumulateDelegate(TestCase):

    def test_accumulate_by_anywhere(self):
        expected_request = Request(host="required_host")
        flow_one = build_flow(request=expected_request)
        flow_two = build_flow(request=Request(host="not_required_host"))
        flow_three = build_flow(request=Request(content="example@example.com"))

        config = AccumulateFilterConfig(in_send="example@example.com")

        instance = Accumulate(filter_config=config)
        instance.request(flow_one)
        instance.request(flow_two)
        instance.request(flow_three)

        assert len(instance.accumulated_items) == 1

    def test_accumulate_by_request(self):
        expected_request = Request(host="required_host")
        flow_one = build_flow(request=expected_request)
        flow_two = build_flow(request=Request(host="not_required_host"))

        config = AccumulateFilterConfig(request=expected_request)

        instance = Accumulate(filter_config=config)
        instance.request(flow_one)
        instance.request(flow_two)

        assert len(instance.accumulated_items) == 1
        assert len(filter(instance.accumulated_items, request=expected_request))

    def test_accumulate_by_response(self):
        expected_response = Response(content="required response")
        flow_one = build_flow(response=expected_response)
        flow_two = build_flow(response=Response(content="not required response"))

        config = AccumulateFilterConfig(response=expected_response)

        instance = Accumulate(filter_config=config)
        instance.response(flow_one)
        instance.response(flow_two)

        assert len(instance.accumulated_items) == 1
        assert len(filter(instance.accumulated_items, response=expected_response))

    def test_accumulate_by_request_and_response(self):
        expected_request = Request(host="required_host")
        expected_response = Response(content="required response")
        flow_one = build_flow(request=expected_request, response=expected_response)
        flow_two = build_flow(
            request=Request(host="not_required_host"),
            response=Response(content="not required response")
        )

        config = AccumulateFilterConfig(
            request=expected_request,
            response=expected_response
        )

        instance = Accumulate(filter_config=config)
        instance.request(flow_one)
        instance.response(flow_one)
        instance.request(flow_two)
        instance.response(flow_two)

        assert len(instance.accumulated_items) == 1
        assert len(filter(instance.accumulated_items, request=expected_request, response=expected_response))
