from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from rikki.appium.common import AppiumUtils, Direction, SwipeSpeed


class IOSXCUITestUtils(AppiumUtils):

    def __init__(self, driver: WebDriver, wait_time: int = 1) -> None:
        super().__init__(driver, wait_time)
        self._directions = {
            Direction.UP: "up",
            Direction.DOWN: "down",
            Direction.LEFT: "left",
            Direction.RIGHT: "right"
        }

    def relaunch_app(self):
        self._driver.launch_app()

    def swipe(self, element: Optional[object] = None, direction: Direction = Direction.DOWN,
              speed: SwipeSpeed = SwipeSpeed.MEDIUM):
        if element:
            self._driver.execute_script('mobile: scroll',
                                        {
                                            'direction': self._directions[direction],
                                            'element': f"{element}"
                                        }
                                        )
        else:
            self._driver.execute_script('mobile: scroll', {'direction': self._directions[direction]})

    @staticmethod
    def support(driver: WebDriver) -> bool:
        platform = driver.desired_capabilities['desired']['platformName']
        automation = driver.desired_capabilities['desired']['automationName']

        return platform == "iOS" and automation == "XCUITest"
