from typing import Optional

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from rikki.appium.common import AppiumUtils, Direction, SwipeSpeed


class AndroidUiAutomator2Utils(AppiumUtils):

    def relaunch_app(self):
        self._driver.launch_app()

    def swipe(
            self,
            element: Optional[object] = None,
            direction: Direction = Direction.DOWN,
            speed: SwipeSpeed = SwipeSpeed.MEDIUM
    ):
        if direction == Direction.UP:
            self.__do_swipe(0, speed.value, element)
        if direction == Direction.DOWN:
            self.__do_swipe(0, -speed.value, element)
        if direction == Direction.LEFT:
            self.__do_swipe(-speed.value, 0, element)
        if direction == Direction.RIGHT:
            self.__do_swipe(speed.value, 0, element)

    def __do_swipe(self, x_offset: int, y_offset: int, element=None):
        if not element:
            element = self._driver.find_elements_by_xpath('//*')[0]

        if element:
            actions = ActionChains(self._driver)
            actions.click_and_hold(element)
            actions.move_by_offset(x_offset, y_offset)
            actions.perform()

    def enable_proxy(self):
        """
        Requires Appium Service to be started with `--relaxed-security`
        Will try to setup proxy on the device and relaunch app.
        """
        self._driver.execute_script("mobile: shell", "am start -a android.settings.WIRELESS_SETTINGS")
        self.tap(By.XPATH, "//*[contains(@text,'AndroidWifi')]")
        self.tap(By.ID, "Settings")
        self.tap(By.ID, "Modify")
        self.tap(By.ID, "com.android.settings:id/proxy_settings")
        self.tap(By.XPATH, "//*[contains(@text,'Manual')]")
        self.enter(By.ID, "com.android.settings:id/proxy_hostname", "10.0.2.2")
        self.enter(By.ID, "com.android.settings:id/proxy_port", "8080")
        self.tap(By.ID, "android:id/button1")
        self.relaunch_app()

    @staticmethod
    def support(driver: WebDriver) -> bool:
        platform = driver.desired_capabilities['desired']['platformName']
        automation = driver.desired_capabilities['desired']['automationName']

        return platform == "Android" and automation == "UiAutomator2"
