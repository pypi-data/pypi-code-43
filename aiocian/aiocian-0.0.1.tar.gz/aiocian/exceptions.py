from typing import Sequence


class CianException(Exception):
    pass


class IncorrectPlaces(CianException):
    def __init__(self, action: str, places: Sequence[str]):
        super().__init__(f"Cannot set places {','.join(places)} for {action}")
        self.action = action
        self.places = places
