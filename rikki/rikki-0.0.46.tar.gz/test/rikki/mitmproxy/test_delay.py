import time
from unittest import TestCase

from rikki.mitmproxy.delegate_delay import DelayConfig, Delay
from rikki.mitmproxy.model import Request
from test.rikki.mitmproxy.utils import build_flow


class TestDelay(TestCase):

    def test_delay(self):
        request = Request(host="test_host")

        config = DelayConfig(request=request, delay=1)

        instance = Delay(config=config)

        flow = build_flow(request=request)

        instance.response(flow)

        assert flow.intercepted, "The flow hasn't been intercepted"

        time.sleep(4)

        assert not flow.intercepted, "The flow hasn't been resumed"
