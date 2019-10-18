'''Unit tests'''

import os
import io
from collections import deque

import requests

from cert_session import Session, _create_certifi_temp


def get_lines_from_file(path):
    with open(path) as fh:
        return fh.readlines()


def get_line_count_path(path):
    with open(path) as fh:
        return get_line_count_fh(fh)


def get_line_count_fh(fh):
    lines = 0

    for _ in fh:
        lines += 1

    return lines


def test_get_line_count_fh():
    fh = io.StringIO('Line1\nLine2\nLine3\n')
    assert get_line_count_fh(fh) == 3


def test_get_line_count_fh_unterminated():
    fh = io.StringIO('Line1\nLine2\nLine3')
    assert get_line_count_fh(fh) == 3


def test_create_certifi_temp(cert_path):
    tmp_path = _create_certifi_temp(cert_path)
    assert tmp_path

    with open(tmp_path) as ftmp:
        tail_lines = list(deque(ftmp, maxlen=get_line_count_path(cert_path)))

    assert tail_lines == get_lines_from_file(cert_path)
    os.unlink(tmp_path)


def test_cert_session(cert_path):
    sess = Session(cert_path)
    assert sess
    assert isinstance(sess, type(requests.session()))

    path = sess.verify
    assert os.path.exists(path)

    sess.__del__()
    assert not os.path.exists(path)
