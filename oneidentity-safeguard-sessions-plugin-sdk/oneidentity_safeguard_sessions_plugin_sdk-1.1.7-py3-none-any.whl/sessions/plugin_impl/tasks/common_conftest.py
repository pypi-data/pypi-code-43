#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
from configparser import ConfigParser
from contextlib import contextmanager
import os
import pytest
import vcr
from vcr.request import Request


SITE_PARAMETER_FILENAMES = ('site_parameters.ini', 'site_parameters_custom.ini')


@contextmanager
def capture_suspended():
    capture_manager = pytest.config.pluginmanager.getplugin('capturemanager')
    capture_manager.suspend_global_capture(in_=True)
    try:
        yield
    finally:
        capture_manager.resume_global_capture()


@pytest.fixture
def interactive(request):
    backend_service = request.config.getoption('backend_service')

    class InteractiveServices(object):
        def message(self, msg, *args):
            if backend_service == 'replay':
                return

            with capture_suspended():
                self._print_msg(msg, *args)

        def askforinput(self, msg, * args):
            inputRequest = Request(method='GET', uri='http://keyboard/{}'.format(msg), body='', headers={})

            if backend_service == 'replay':
                cassette = request.getfixturevalue('vcr_cassette')
                return cassette.play_response(inputRequest)['body']

            with capture_suspended():
                self._print_msg(msg, *args)
                userinput = input("> ")  # noqa: F821

            if backend_service == 'record':
                cassette = request.getfixturevalue('vcr_cassette')
                response = {'body': userinput, 'status': {'code': 200, 'message': 'OK'}}
                cassette.append(inputRequest, response)

            return userinput

        def _print_msg(self, msg, *args):
            print("\n{}\n# {}\n{}\n".format(80 * '*', msg % args, 80 * '*'))

    return InteractiveServices()


@pytest.fixture(autouse=True)
def fake_backend(request):

    backend_service = request.config.getoption('backend_service')
    if backend_service == "replay":
        request.config.option.vcr_record_mode = 'none'
        request.getfixturevalue('vcr_cassette')
    elif backend_service == "record":
        request.config.option.vcr_record_mode = 'all'
        cassette = request.getfixturevalue('vcr_cassette')
        cassette.data = []
    elif backend_service != "use":
        raise ValueError()


def pytest_addoption(parser):
    parser.addoption("--backend-service", action="store", default="replay",
                     choices=['record', 'replay', 'use'],
                     help="How to behave wrt the external service: record, replay or use")


@pytest.fixture
def site_parameters(request):
    cp = ConfigParser()
    assert cp.read([os.path.join(os.path.dirname(request.fspath), filename) for filename in SITE_PARAMETER_FILENAMES])
    yield dict(cp.items('site'))
