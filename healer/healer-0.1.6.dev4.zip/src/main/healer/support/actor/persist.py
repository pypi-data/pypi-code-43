"""
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from healer.support.typing import override

from .proper import ProperActor
from .proper import proper_receive_type

frozen = dataclass(frozen=True)


@frozen
class PersistMissive:
    content:Any = None


@frozen
class PersistCommand(PersistMissive):
    pass


@frozen
class PersistEvent(PersistMissive):
    pass


@frozen
class PersistSnapshot(PersistMissive):
    pass


class PersistActor(ProperActor):
    """
    """

    @proper_receive_type
    def on_command(self, message:PersistCommand):
        pass

    @proper_receive_type
    def on_event(self, message:PersistEvent):
        pass

    @proper_receive_type
    def on_snapshot(self, message:PersistEvent):
        pass

    @override
    def on_start(self):
        pass

    @override
    def on_stop(self):
        pass
