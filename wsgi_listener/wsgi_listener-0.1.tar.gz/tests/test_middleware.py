import logging
from io import BytesIO
from wsgiref.util import setup_testing_defaults
from pytest import fixture

from .context import WSGIListenerMiddleware, DEFAULT_LISTENER_LOG_NAME


@fixture
def environ_factory():
    def _environ_factory(**kwargs):
        environ = dict(kwargs)
        setup_testing_defaults(environ)
        return environ
    return _environ_factory


@fixture
def environ_with_request_body_factory(environ_factory):
    def _factory(request_body: BytesIO = None, environ: dict = None):
        if not environ:
            environ = environ_factory()

        if request_body:
            environ['wsgi.input'] = request_body
            environ['CONTENT_LENGTH'] = request_body.getbuffer().nbytes

        return environ
    return _factory


def app(environ, start_fn):
    start_fn('200 OK', [('Content-Type', 'text/plain')])
    yield b'Hello World!\n'


def start_response(status_code, headers, exc_info=None):
    return status_code, headers, exc_info


def test_middleware_passthrough(environ_factory):
    environ = environ_factory()
    wrapped_app = WSGIListenerMiddleware(app)
    rv = wrapped_app(environ, start_response)
    assert next(rv) == b'Hello World!\n'


def test_middleware_default_response_listener(caplog, environ_factory):
    environ = environ_factory()
    wrapped_app = WSGIListenerMiddleware(app)
    with caplog.at_level(logging.INFO, logger=DEFAULT_LISTENER_LOG_NAME):
        wrapped_app(environ, start_response)
    assert caplog.text


def test_listeners(environ_with_request_body_factory):
    # noinspection PyAttributeOutsideInit,PyShadowingNames
    class EchoRequestListener:
        def handle(self, environ: dict, request_body: bytes, **kwargs):
            self.environ = environ
            self.request_body = request_body

    # noinspection PyAttributeOutsideInit,PyShadowingNames
    class EchoResponseListener:
        def handle(self, status_code: int, environ: dict, content_length: int, response_body: bytes,
                   processing_time: float, **kwargs):
            self.status_code = status_code
            self.environ = environ
            self.content_length = content_length
            self.response_body = response_body
            self.processing_time = processing_time

    request_listener = EchoRequestListener()
    response_listener = EchoResponseListener()
    body = BytesIO(b'Test')
    environ = environ_with_request_body_factory(body)
    wrapped_app = WSGIListenerMiddleware(app, request_listeners=[request_listener],
                                         response_listeners=[response_listener])

    wrapped_app(environ, start_response)

    assert request_listener.environ is environ
    assert request_listener.request_body == b'Test'

    assert response_listener.status_code
    assert response_listener.environ is environ
    assert response_listener.response_body == b'Hello World!\n'
    assert response_listener.content_length == len(b'Hello World!\n')
    assert response_listener.processing_time
