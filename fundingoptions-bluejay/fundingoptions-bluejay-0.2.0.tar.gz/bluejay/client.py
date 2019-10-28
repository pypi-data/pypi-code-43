from .backend.command import SendEvent
from .backend.interface import IBackend
from .interface import IEvent


class Client:
    def __init__(self, backend: IBackend):
        self.backend = backend

    def send(self, event: IEvent) -> None:
        event_name = event.event_name
        message = event.as_dict()
        self.send_raw(event_name=event_name, message=message)

    def send_raw(self, event_name: str, message: dict) -> None:
        self.backend.send(SendEvent(payload=message, event_name=event_name))
