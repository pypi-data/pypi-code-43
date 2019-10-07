
from healer.support.network import *


def test_private_address():
    print()
    address = NetworkSupport.private_address()
    print(f"private address: {address}")


def test_public_address():
    print()
    address = NetworkSupport.public_address()
    print(f"public address: {address}")


def test_host_name():
    print()
    print(NetworkSupport.host_name())
