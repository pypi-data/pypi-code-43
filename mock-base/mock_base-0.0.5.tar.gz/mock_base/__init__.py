from __future__ import annotations
from typing import Dict, Optional, List, Callable

from ._firestore import mockstore
from ._messaging import messaging


_apps: Dict[str, MockApp] = {}
_DEFAULT_APP_NAME = '[DEFAULT]'

__all__ = [
    "Message",
    "Notification",
    "MockClient"
]

Message = messaging.Message
Notification = messaging.Notification
MockClient = mockstore.MockClient


class MockApp:
    
    def __init__(self, name):
        self.name = name
        self.__mock_store: Optional[MockClient] = None
        self.__listeners: List[Callable[[object], None]] = []
    
    def set_firestore(self, client: MockClient):
        # assert self.__firestore is None, """
        # the firestore client of this app: "{}" is instantiated several times""".format(self.name)
        self.__mock_store = client
    
    @property
    def firestore(self) -> MockClient:
        return self.__mock_store
    
    def add_listener(self, fun: Callable[[Message], None]) -> None:
        self.__listeners.append(fun)
    
    def notify_listeners(self, message: Message):
        for l in self.__listeners:
            l(message)


def initialize_mock_app(name=_DEFAULT_APP_NAME) -> MockApp:

    if name in _apps.keys():
        raise ValueError("mock app named \"{}\" already exists.".format(name))
    else:
        _a = MockApp(name)
        _apps.update({
            name: _a
        })
    return _a


def get_mock_app(name=_DEFAULT_APP_NAME) -> MockApp:
    if name in _apps.keys():
        _a = _apps.get(_DEFAULT_APP_NAME)
        if _a is None:
            raise ValueError("app not initialized")
        return _a
    else:
        raise ValueError("mock app named \"{}\" already exists.".format(name))


def delete_mock_app(app: MockApp):
    _apps.pop(app.name)
