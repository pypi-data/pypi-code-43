from __future__ import annotations

import pykka

from datetime import datetime
from dataclasses import dataclass
from mashumaro.types import SerializationStrategy
from mashumaro.serializer.msgpack import DataClassMessagePackMixin
# from healer.support.wired import Wired
# from healer.support.actor.wired import WiredActorRef


class PlainActorRef(SerializationStrategy):

    def _serialize(self, actor_ref: pykka.ActorRef) -> str:
        return actor_ref.actor_urn

    def _deserialize(self, value: str) -> pykka.ActorRef:
        actor_ref = pykka.ThreadingActor().start()
        actor_ref.stop()
        return actor_ref


class FormattedDateTime(SerializationStrategy):

    def __init__(self, fmt):
        self.fmt = fmt

    def _serialize(self, actor_ref: datetime) -> str:
        return actor_ref.strftime(self.fmt)

    def _deserialize(self, value: str) -> datetime:
        return datetime.strptime(value, self.fmt)


frozen = dataclass(frozen=True)


@frozen
class SomeBaseOne():
# class SomeBaseOne(Wired):
    """
    """


@frozen
class SomeBaseTwo(SomeBaseOne):
    """
    """


@frozen
class SomeValue(SomeBaseOne):
#     actor_ref:WiredActorRef()  # PlainActorRef()
    short: FormattedDateTime(fmt='%d%m%Y%H%M%S')  # = datetime.now()
    verbose: FormattedDateTime(fmt='%A %B %d, %Y, %H:%M:%S')  # = datetime.now()


actor_ref = pykka.ThreadingActor().start()
actor_ref.stop()

formats = SomeValue(
    actor_ref=actor_ref,
    short=datetime(2019, 1, 1, 12),
    verbose=datetime(2019, 1, 1, 12),
)

print(formats)

result = formats.to_msgpack()

print(result)

# assert SomeValue.from_msgpack(result) == formats
