from typing import Any, Hashable


class Tree(dict):
    """Creates keys as needed in a nested Tree structure."""

    def __missing__(self, key: Hashable) -> Any:
        value = self[key] = type(self)()
        return value

    def as_dict(self) -> dict:
        """Converts all levels of the tree to standard Python dictionaries."""
        return {
            key: value.as_dict() if isinstance(value, self.__class__) else value
            for key, value in self.items()
        }
