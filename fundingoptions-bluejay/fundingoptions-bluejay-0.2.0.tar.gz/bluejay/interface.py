from typing_extensions import Protocol


class IEvent(Protocol):
    event_name = ""  # type: str

    def as_dict(self) -> dict:
        ...
