

from healer.cluster.hood.mdns import *


def test_address():
    print()
    address = ipaddress.ip_address(b'\x7f\x00\x00\x01')
    print(f"address: {address} {str(address)}")
