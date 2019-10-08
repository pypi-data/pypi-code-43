from unittest import TestCase
from test.rikki.mitmproxy.utils import build_flow
from rikki.mitmproxy.model import Request
from rikki.mitmproxy.util import filter
from json import JSONEncoder


class TestFlowFilter(TestCase):

    def test_plain_host(self):
        flow = build_flow(request=Request(host="www.google.com"))

        result = filter([flow], request=Request(host="google"))

        assert len(result) == 0

        result = filter([flow], request=Request(host=".*google"))

        assert len(result) == 0

        result = filter([flow], request=Request(host=".*google.*"))

        assert len(result) == 1

    def test_plain_host_and_host_header(self):
        flow = build_flow(request=Request(host="127.0.0.1", headers={"Host": "www.google.com"}))

        result = filter([flow], request=Request(host="google"))

        assert len(result) == 0

        result = filter([flow], request=Request(host=".*google"))

        assert len(result) == 0

        result = filter([flow], request=Request(host=".*google.*"))

        assert len(result) == 1

    def test_plain_content(self):
        flow = build_flow(
            request=Request(
                host="127.0.0.1",
                content="hello"
            )
        )

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="no way"
            )
        )

        self.assertEqual(len(result), 0)

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="hello"
            )
        )

        self.assertEqual(len(result), 1)

    def test_plain_host_and_json_content_json_dict(self):
        flow = build_flow(
            request=Request(
                host="127.0.0.1",
                content="{\"host\": \"www.google.com\", \"name\": \"rikki\"}"
            )
        )

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="?{\"evil\": \"www.yandex.com\"}"
            )
        )

        self.assertEqual(len(result), 0)

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="?{\"host\": \"www.google.com\"}"
            )
        )

        self.assertEqual(len(result), 1)

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="?{\"host\": \"www.google.com\", \"name\": \"rikki\"}"
            )
        )

        self.assertEqual(len(result), 1)

    def test_plain_host_and_json_content_json_array(self):
        flow = build_flow(
            request=Request(
                host="127.0.0.1",
                content="[{\"host\": \"www.google.com\", \"name\": \"rikki\"}]"
            )
        )

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="[{\"evil\": \"www.yandex.com\"}]"
            )
        )

        self.assertEqual(len(result), 0)

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="[{\"host\": \"www.google2.com\"}]"
            )
        )

        self.assertEqual(len(result), 0)

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="[{\"host\": \"www.google.com\", \"name\": \"rikki\"}]"
            )
        )

        self.assertEqual(len(result), 1)

    def test_nested_json_object_in_content(self):
        flow = build_flow(
            request=Request(
                host="127.0.0.1",
                content="{\"host\": \"www.google.com\", \"config\": { \"name\": \"rikki\", \"lang\": \"pyhton\" }}"
            )
        )

        result = filter(
            [flow],
            request=Request(
                host="127.0.0.1",
                content="?{\"config\": {\"name\": \"rikki\"}}"
            )
        )

        self.assertEqual(len(result), 1)

    def test_nested_object_in_array(self):
        flow = build_flow(
            request=Request(
                content=JSONEncoder().encode(
                    {
                        "param": "",
                        "configs": [
                            {
                                "name": "rikki",
                                "lang": "python",
                                "version": "unknown"
                            },
                            {
                                "name": "undefined",
                                "lang": "undefined"
                            }
                        ]
                    }
                )
            )
        )

        request = Request(
            content="?" + JSONEncoder().encode(
                {
                    "param": "",
                    "configs": [
                        {
                            "name": "rikki",
                            "lang": "python"
                        }
                    ]
                }
            )
        )

        result = filter([flow], request)

        self.assertEqual(len(result), 1)
