from . import _DEFAULT_APP_NAME, _apps, MockApp, _MockApp
from .messaging import Message
from typing import List
import json
import base64
import random
import string


class FakeDevice:
    
    def __init__(self, uid: str, app: MockApp = None):
        assert uid is not None, "The fake device needs a UID to belong to it"
        self.app = None
        if app is None:
            self.app: MockApp = _apps.get(_DEFAULT_APP_NAME)
            assert self.app is not None, "the default application has not been initialized"
        else:
            self.app: MockApp = app
        if isinstance(self.app, _MockApp):
            self.app.add_listener(self._listener)
        self.uid: str = uid
        self._primary = random.choices(string.ascii_lowercase)
        self._messages: List[Message] = []
    
    @staticmethod
    def __tokenize(s: dict):
        j = json.dumps(s)
        return base64.encodebytes(j.encode()).decode()
    
    def get_id_token(self):
        claim = {
            "uid": self.uid,
            "app": self.app.name
        }
        return self.__tokenize(claim)
    
    def device_id_token(self) -> str:
        claim = {
            "app": self.app.name,
            "primary": self._primary,
            "uid": self.uid
        }
        return self.__tokenize(claim)
    
    def _listener(self, message: Message):
        if message.token == self.device_id_token():
            self._messages.append(message)
    
    @property
    def messages(self) -> List[Message]:
        return self._messages
