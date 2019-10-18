import socket
import pytest
from pyraii.resource_concept import is_resource


@pytest.mark.parametrize("resource_type", [socket.socket])
def test_resources_types(resource_type):
    assert is_resource(resource_type)


@pytest.mark.parametrize("resource_type", [int, list, dict, Exception])
def test_non_resources_types(resource_type):
    assert not is_resource(resource_type)
