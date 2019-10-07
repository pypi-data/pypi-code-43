
import os
import time
import shutil
import atexit
import tempfile

from healer.cluster.files.actor import *
from healer.support.actor.master import MasterActor


class DummyMaster(MasterActor):
    ""

    @override
    def on_start(self):
        super().on_start()
        file_store = tempfile.mkdtemp(prefix="store-", suffix=".db")
        atexit.register(shutil.rmtree, file_store)
        self.files_actor = self.worker_start(FilesActor, file_store)


def test_actor():
    print()
    master_one = DummyMaster.start()
    master_two = DummyMaster.start()
    time.sleep(1)
    master_one.stop()
    master_two.stop()
