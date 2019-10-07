"""
Hierarchically related actors: master/project/worker pattern
"""

from __future__ import annotations

from typing import Any
from typing import List
from typing import Type

from healer.support.typing import override

from .proper import ProperActor
from .proper import ProperRef


class Master:
    ""
    master_namer = "master@actor"


class MasterActor(ProperActor):
    """
    tree root actor
    """

    worker_actor_list:List[ProperRef]

    @override
    def on_start(self):
        self.worker_actor_list = list()

    @override
    def on_stop(self):
        for actor in reversed(self.worker_actor_list):
            actor.stop()

    def worker_start(self, worker_type:Type[WorkerActor], **kwargs) -> ProperRef:
        assert issubclass(worker_type, WorkerActor), f"need worker: {worker_type}"
        kwargs[Master.master_namer] = self.actor_ref
        worker_actor = worker_type.start(**kwargs)
        self.worker_actor_list.append(worker_actor)
        return worker_actor

    def worker_stop(self, worker_actor:ProperRef) -> None:
        if worker_actor in self.worker_actor_list:
            self.worker_actor_list.remove(worker_actor)
            worker_actor.stop()

    def query_worker(self, message:Any) -> None:
        "ask report from downstream"
        for worker_actor in self.worker_actor_list:
            self.query(worker_actor, message)


class WorkerActor(ProperActor):
    """
    tree leaf actor
    """

    master_actor:ProperRef  # supervisor, if any

    def __init__(self, **kwargs) -> None:
        master_actor = kwargs.pop(Master.master_namer, None)
        self.master_actor = master_actor
        super().__init__(**kwargs)
        if master_actor is not None:
            assert isinstance(master_actor, ProperRef), f"need ref: {master_actor}"
            master_class = master_actor.actor_class
            assert issubclass(master_class, MasterActor), f"need master: {master_class}"

    def query_master(self, message:Any) -> None:
        "ask report from upstream"
        self.query(self.master_actor, message)


class ProjectActor(MasterActor, WorkerActor, ProperActor):
    """
    tree branch actor
    """
