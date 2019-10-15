from typing import Union

from django_actionable_messages.message_card.utils import OSType
from django_actionable_messages.utils import CardElement


class Header(CardElement):
    def __init__(self, name: str, value: Union[str, int]):
        self._data = {
            "name": name,
            "value": value
        }
        super().__init__()

    def get_name(self):
        return self._data["name"]


class Fact(CardElement):
    def __init__(self, name: str, value: str):
        self._data = {
            "name": name,
            "value": value
        }
        super().__init__()


class HeroImage(CardElement):
    def __init__(self, url: str, title: str = None):
        self._data = {
            "image": url
        }
        if title is not None:
            self.set_title(title)
        super().__init__()

    def set_url(self, url: str):
        self._data["image"] = url

    def set_title(self, title: str):
        self._data["title"] = title


class InputChoice(CardElement):
    def __init__(self, name: str, value: Union[str, int]):
        self._data = {
            "display": name,
            "value": value
        }
        super().__init__()

    def get_value(self):
        return self._data["value"]


class ActionTarget(CardElement):
    def __init__(self, os_type: OSType, url: str):
        self._data = {
            "os": os_type.value,
            "uri": url
        }
        super().__init__()

    def get_os(self):
        return self._data["os"]
