
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import List
from sidecar.sandbox_error import SandboxError


class StatusMaintainer:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_qualiy_status(self, status: str):
        raise NotImplementedError

    @abstractmethod
    def add_sandbox_error(self, error: SandboxError):
        raise NotImplementedError
