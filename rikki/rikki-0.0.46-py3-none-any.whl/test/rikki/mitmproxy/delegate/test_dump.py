from typing import List
from unittest import TestCase

from mitmproxy import http

from rikki.mitmproxy.delgate.dump import DumpWriterConfig, DumpWriter, DumpWriterDelegate
from test.rikki.mitmproxy.utils import build_flow
from rikki.mitmproxy.model import Request, Response


class TestDump(TestCase):

    def test_should_dump_filtered_requests(self):
        flow_one = build_flow(request=Request(host="http://should_be_in_results"))
        flow_two = build_flow(request=Request(host="http://should_be_in_results"))
        flow_three = build_flow(request=Request(host="http://should_not_be_in_results"))
        flow_for = build_flow(request=Request(host="http://should_not_be_in_results"))

        config = DumpWriterConfig(
            path="",
            request=Request(host="http://should_be_in_results"),
            dump_writer=_MockDumpWriter
        )

        dump = DumpWriterDelegate(config=config)

        dump.request(flow_one)
        dump.request(flow_two)
        dump.request(flow_three)
        dump.request(flow_for)

        dump.shutdown()

        # noinspection PyTypeChecker
        dump_writer: _MockDumpWriter = dump.writer

        self.assertEqual(len(dump_writer.results), 2)
        self.assertIn(flow_one, dump_writer.results)
        self.assertIn(flow_two, dump_writer.results)

    def test_should_close_dump_writer(self):
        config = DumpWriterConfig(
            path="",
            dump_writer=_MockDumpWriter
        )

        dump = DumpWriterDelegate(config=config)

        dump.shutdown()

        # noinspection PyTypeChecker
        dump_writer: _MockDumpWriter = dump.writer

        self.assertTrue(dump_writer.closed)


class _MockDumpWriter(DumpWriter):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.results: List[http.HTTPFlow] = []
        self.closed: bool = False

    def write_flows(self, flows: List[http.HTTPFlow]):
        self.results.extend(flows)

    def close(self):
        self.closed = True
