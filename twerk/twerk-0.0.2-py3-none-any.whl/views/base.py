from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty

import log
from splinter import Browser


class View(ABC):
    def __init__(self, browser: Browser, *, goto: bool = True):
        self._browser = browser

        if self._active:
            return

        if goto:
            self._goto()
        else:
            log.debug(f"Current URL: {self._browser.url}")
            raise RuntimeError(f"Expected {self} to already be active")

        if self._active:
            return

        log.debug(f"Current URL: {self._browser.url}")
        raise RuntimeError(f"Failed to navigate to {self}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._url}>"

    @abstractproperty
    def _url(self) -> str:
        raise NotImplementedError

    @property
    def _active(self) -> bool:
        return self._browser.url == self._url

    @abstractmethod
    def _goto(self) -> View:
        raise NotImplementedError
