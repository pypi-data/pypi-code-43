from typing import Any, Dict


class DictDaora(Dict[str, Any]):
    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as error:
            raise AttributeError(*error.args)

    def set(self, key: str, value: Any) -> None:
        self[key] = value

    def unset(self, key: str, *args: Any) -> None:
        try:
            self.pop(key, *args)
        except KeyError as error:
            raise AttributeError(*error.args)
