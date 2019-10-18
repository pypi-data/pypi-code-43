'''Test fixtures'''

import os

import pytest

@pytest.fixture
def cert_path():
    yield os.path.join(_get_script_dir(), 'TestCertCA.crt')


def _get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))
