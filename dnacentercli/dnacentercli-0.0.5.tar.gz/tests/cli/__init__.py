# -*- coding: utf-8 -*-
"""DNACenterAPI fixtures and tests.

Copyright (c) 2019 Cisco and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from click.testing import CliRunner
from dnacentercli.cli import main as dnacentercli
from tests.environment import (
    DNA_CENTER_USERNAME, DNA_CENTER_PASSWORD,
    DNA_CENTER_ENCODED_AUTH, DNA_CENTER_VERSION,
    DNA_CENTER_BASE_URL,
    DNA_CENTER_VERIFY,
    DNA_CENTER_DEBUG,
    DNA_CENTER_SINGLE_REQUEST_TIMEOUT,
    DNA_CENTER_WAIT_ON_RATE_LIMIT,
)
import pytest


# Fixtures
@pytest.fixture(scope='function')
def runner(request):
    return CliRunner()


@pytest.fixture(scope='session')
def cli():
    return dnacentercli


@pytest.fixture(scope='session')
def auth_options():
    result_username = DNA_CENTER_USERNAME is not None and ["--username", "{}".format(DNA_CENTER_USERNAME)] or []
    result_password = DNA_CENTER_PASSWORD is not None and ["--password", "{}".format(DNA_CENTER_PASSWORD)] or []
    result_encoded_auth = DNA_CENTER_ENCODED_AUTH is not None and ["--encoded_auth", "{}".format(DNA_CENTER_ENCODED_AUTH)] or []
    result = [
        "-v", "{}".format(DNA_CENTER_VERSION),
        *result_username,
        *result_password,
        *result_encoded_auth,
        "--base_url", "{}".format(DNA_CENTER_BASE_URL),
        "--verify", "{}".format(DNA_CENTER_VERIFY),
        "--debug", "{}".format(DNA_CENTER_DEBUG),
        "--single_request_timeout", "{}".format(DNA_CENTER_SINGLE_REQUEST_TIMEOUT),
        "--wait_on_rate_limit", "{}".format(DNA_CENTER_WAIT_ON_RATE_LIMIT),
        "--verify", "{}".format(DNA_CENTER_VERIFY),
        "-n"
    ]
    return result
