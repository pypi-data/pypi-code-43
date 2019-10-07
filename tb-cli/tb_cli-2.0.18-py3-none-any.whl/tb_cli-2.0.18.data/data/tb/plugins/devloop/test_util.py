import json
from unittest import mock

from tb import ColoredTerminal
from .util import print_local_line

term = ColoredTerminal()


def test_print_local_line():
    with mock.patch('tb.term.print') as print:
        print_local_line(term, 'blah')
        assert print.call_args[0][0] == "blah"


def test_print_local_line_with_json():
    with mock.patch('tb.term.print') as print:
        print_local_line(term, "foo INFO {}".format(json.dumps({
            '@timestamp': '17:24:45.379',
            'level': 'INFO',
            'message': 'hi'})))
        assert print.call_args[0][0] == "17:24:45.379 [?:?:?] () INFO hi"
