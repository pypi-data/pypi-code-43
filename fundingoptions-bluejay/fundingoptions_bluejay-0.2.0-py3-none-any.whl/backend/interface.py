from typing import TypeVar

from typing_extensions import Protocol

from .command import SendEvent, SendResponse

T = TypeVar("T")


class IBackend(Protocol):
    def send(self, message: SendEvent) -> SendResponse:
        ...
