from enum import Enum
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.wait import WebDriverWait


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class SwipeSpeed(Enum):
    SLOW = 200
    MEDIUM = 400
    FAST = 800
    ROCKET_MAN = 1600


class AppiumUtils:

    def __init__(self, driver: WebDriver, wait_time: int = 1) -> None:
        super().__init__()
        self.wait_time = wait_time
        self._driver: WebDriver = driver

    def tap(self, by: By, locator: str, wait_time: Optional[int] = None):
        wait = self._configure_wait(wait_time)
        wait.until(conditions.presence_of_element_located((by, locator))).click()

    def enter(self, by: By, locator: str, text: str, wait_time: Optional[int] = None):
        wait = self._configure_wait(wait_time)
        wait.until(conditions.presence_of_element_located((by, locator))).send_keys(text)

    def wait(self, by: By, locator: str, wait_time: Optional[int] = None):
        wait = self._configure_wait(wait_time)
        wait.until(conditions.presence_of_element_located((by, locator)))

    def relaunch_app(self):
        assert False, "Relaunch app is not implemented"

    def swipe(
            self,
            element: Optional[object] = None,
            direction: Direction = Direction.DOWN,
            speed: SwipeSpeed = SwipeSpeed.MEDIUM
    ):
        assert False, "Swipe is not supported:"

    def _configure_wait(self, wait_time: Optional[int] = None):
        delay = self.wait_time
        if wait_time:
            delay = wait_time
        return WebDriverWait(self._driver, delay)

    @staticmethod
    def support(driver: WebDriver) -> bool:
        """
        :param driver:
        :return: True if this instance of the utils support the context
        """
        return True
