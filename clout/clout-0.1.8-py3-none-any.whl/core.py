import typing_extensions


class Encoder(typing_extensions.Protocol):
    def dumps(self, data) -> str:
        ...

    def loads(self, text: str):
        ...
