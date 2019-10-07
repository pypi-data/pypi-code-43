import time
import inspect

from healer.support.actor.master import *
from dataclasses import dataclass
from healer.support.typing import override


class UpperActor(MasterActor):

    @override
    def on_start(self):
        print(f"on_start: upper")
        super().on_start()
        self.lower_one = self.worker_start(LowerActor, value='one')
        self.lower_two = self.worker_start(LowerActor, value='two')
        self.middle = self.worker_start(MiddleActor, value='middle')

    @override
    def on_stop(self):
        super().on_stop()
        print(f"on_stop: upper")


class LowerActor(WorkerActor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = kwargs['value']

    @override
    def on_start(self):
        print(f"on_start: lower: {self.value}")

    @override
    def on_stop(self):
        print(f"on_stop: lower: {self.value}")


class MiddleActor(ProjectActor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = kwargs['value']

    @override
    def on_start(self):
        super().on_start()
        print(f"on_start: middle: {self.value}")
        self.lower_three = self.worker_start(LowerActor, value='three')

    @override
    def on_stop(self):
        super().on_stop()
        print(f"on_stop: middle: {self.value}")


def test_master_worker():
    print()
    upper = UpperActor.start()
    time.sleep(0.2)
    upper.stop()
