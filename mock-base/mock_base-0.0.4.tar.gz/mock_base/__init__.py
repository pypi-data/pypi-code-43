from __future__ import annotations
from typing import Optional, Dict, Callable, List
from .mockstore.mock import MockClient

from ._app import MockApp

_apps: Dict[str, _MockApp] = {}
_DEFAULT_APP_NAME = '[DEFAULT]'


def initialize_app(name=_DEFAULT_APP_NAME) -> MockApp:

    if name in _apps.keys():
        raise ValueError("mock app named \"{}\" already exists.".format(name))
    else:
        _a = _MockApp(name)
        _apps.update({
            name: _a
        })
    return _a


def get_app(name=_DEFAULT_APP_NAME) -> MockApp:
    if name in _apps.keys():
        _a = _apps.get(_DEFAULT_APP_NAME)
        if _a is None:
            raise ValueError("app not initialized")
        return _a
    else:
        raise ValueError("mock app named \"{}\" already exists.".format(name))


class _MockApp(MockApp):
    
    def __init__(self, name):
        super().__init__(name)
        self.__firestore: Optional[MockClient] = None
        self.__listeners: List[Callable[[object], None]] = []
    
    def set_firestore(self, client: MockClient):
        # assert self.__firestore is None, """
        # the firestore client of this app: "{}" is instantiated several times""".format(self.name)
        self.__firestore = client
        
    @property
    def firestore(self) -> MockClient:
        return self.__firestore
    
    def add_listener(self, fun: Callable[[Message], None]) -> None:
        self.__listeners.append(fun)

    def notify_listeners(self, message: Message):
        for l in self.__listeners:
            l(message)


def delete_app(app: MockApp):
    _apps.pop(app.name)
