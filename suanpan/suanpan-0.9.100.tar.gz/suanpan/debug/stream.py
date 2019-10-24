# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.stream import Stream
from suanpan.utils import env


class StreamTester(Stream):
    def __init__(self, *args, **kwargs):
        env.environ["STREAM_SEND_QUEUE"] = env.environ["STREAM_RECV_QUEUE"]
        super(StreamTester, self).__init__(*args, **kwargs)


tester = StreamTester()


def send(*args, **kwargs):
    return tester.sendMissionMessage(tester.generateMessage(), *args, **kwargs)
