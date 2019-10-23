import pytest
from concurrent.futures import Future

from zaber_motion.call import call, call_sync, call_async
from zaber_motion.events import events
from zaber_motion.protobufs import main_pb2
from zaber_motion import RequestTimeoutException


def test_request_response():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponse()
    call("test/request", request, response)

    assert response.data_pong == 'Hello...'

@pytest.mark.asyncio
async def test_request_response_async():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponse()
    await call_async("test/request", request, response)

    assert response.data_pong == 'Hello...'

def test_request_response_sync():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponse()
    call_sync("test/request", request, response)

    assert response.data_pong == 'Hello...'

def test_request_error():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"
    request.return_error = True

    try:
        response = main_pb2.TestResponse()
        call("test/request", request, response)
        assert False, "No error thrown"
    except RequestTimeoutException as e:
        assert e.message == "Device has not responded in given timeout"
        assert str(e) == "RequestTimeoutException: Device has not responded in given timeout"


def test_request_no_response():
    response = call("test/request_no_response")
    assert response == None


def test_request_long_response():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponseLong()
    call("test/request_long", request, response)

    for i in range(len(response.data_pong)):
        assert response.data_pong[i] == 'Hello...{}'.format(i)


def test_event():
    promise = Future()
    with events.take(1).subscribe(lambda event: promise.set_result(event)):
        call("test/emit_event")

        event = promise.result()
        assert event[0] == "test/event"
        assert event[1].data == "testing event data"
