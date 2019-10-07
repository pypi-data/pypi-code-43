import time
import uuid

from healer.cluster.arkon import *
from pykka._registry import ActorRegistry


def test_actor():
    print()

    count = 2
    delay = 0.5

    cluster_map = dict()

    for index in range(count):
        node_guid = WiredBytes.generate()
        cluster = ClusterActor.start(node_guid=node_guid)
        cluster_map[index] = cluster
        time.sleep(0.1)

    time.sleep(delay)

    print(f"ONE")
    for actor in ActorRegistry.get_all():
        print(actor)

    assert len(ActorRegistry.get_by_class(ClusterActor)) == count

    time.sleep(delay)

    for index in range(count):
        cluster = cluster_map[index]
        cluster.stop()
        time.sleep(0.1)

    print(f"TWO")
    for actor in ActorRegistry.get_all():
        print(actor)
