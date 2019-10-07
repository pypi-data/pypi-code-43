import time
import uuid

from healer.cluster.hood.actor import *
from healer.support.network import NetworkSupport
from healer.support.actor.master import MasterActor
from healer.support.wired.typing import WiredBytes

node_info = NodeInfo(
    guid=WiredBytes.generate(),
    addr=NetworkSupport.private_address(),
    port=22122,
)


class DummyMaster(MasterActor):
    ""

    @override
    def on_start(self):
        super().on_start()
        self.hood_actor = self.worker_start(HoodActor)
        self.hood_actor.tell(HoodTalk.IssueEnable(node_info))

    @override
    def on_stop(self):
        self.hood_actor.tell(HoodTalk.IssueDisable(node_info))
        super().on_stop()


def test_actor():
    print()
    master = DummyMaster.start()
    time.sleep(1)
    master.stop()
