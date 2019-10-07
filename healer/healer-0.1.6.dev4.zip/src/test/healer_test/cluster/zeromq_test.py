
from urllib.parse import urlparse

from healer.cluster.zeromq import *


def test_local_bind():
    print()

    router_map = dict()

    for index in range(10):
        router = SupportZMQ.socket_router()
        router_map[index] = router
        point = SupportZMQ.perform_local_bind(router)
        print(f"point: {point}")
        point_url = urlparse(point)
        print(f"point_url: {point_url.scheme} {point_url.hostname} {point_url.port}")

