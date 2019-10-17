import os
from .utils import ColorPrint


class EMConfig(object):
    def __init__(
        self,
        SYSTEM_EVENT_NAME: str,
        SYSTEM_EVENT_URL: str,
        SYSTEM_EVENT_TOKEN: str,
        em_notify: bool = False,
        debug: bool = True,
    ):
        self.system_name = SYSTEM_EVENT_NAME
        self.system_url = SYSTEM_EVENT_URL
        self.token = SYSTEM_EVENT_TOKEN
        self.em_notify = str(em_notify)
        self.debug = str(debug)
        self.init_environ_settings()

    def init_environ_settings(self) -> None:
        os.environ["SYSTEM_EVENT_NAME"] = self.system_name
        os.environ["SYSTEM_EVENT_URL"] = self.system_url
        os.environ["SYSTEM_EVENT_TOKEN"] = self.token
        os.environ["SYSTEM_EM_NOTIFIER"] = self.em_notify
        os.environ["DEBUG"] = self.debug
