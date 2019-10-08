from typing import List, Optional

from appium.webdriver.appium_service import AppiumService
from behave.configuration import Configuration as BehaveConfiguration
from behave.model import Feature, Tag, Scenario, Table, Row
from selenium.webdriver.remote.webdriver import WebDriver

from rikki.appium.common import AppiumUtils
from rikki.mitmproxy.plugin import ProxyPlugin


class Configuration(BehaveConfiguration):

    def __init__(self, command_args=None, load_config=True, verbose=None, **kwargs):
        super().__init__(command_args, load_config, verbose, **kwargs)
        self.proxy: Optional[ProxyPlugin] = None


class Context:
    """
    Provide typed access to Behave context object.
    More documentation can'be founded there https://behave.readthedocs.io/en/latest/context_attributes.html
    """

    def __init__(
            self,
            config: Optional[Configuration] = None,
            aborted: Optional[bool] = None,
            failed: Optional[bool] = None,
            feature: Optional[Feature] = None,
            tags: Optional[List[Tag]] = None,
            active_outline: Optional[Row] = None,
            scenario: Optional[Scenario] = None,
            table: Optional[Table] = None,
            text: Optional[str] = None,
            proxy: Optional[ProxyPlugin] = None,
            browser: Optional[WebDriver] = None,
            appium: Optional[AppiumService] = None,
            appium_utils: Optional[AppiumUtils] = None
    ) -> None:
        super().__init__()
        self.config: Optional[Configuration] = config
        self.aborted: Optional[bool] = aborted
        self.failed: Optional[bool] = failed
        self.feature: Optional[Feature] = feature
        self.tags: Optional[List[Tag]] = tags
        self.active_outline: Optional[Row] = active_outline
        self.scenario: Optional[Scenario] = scenario
        self.table: Optional[Table] = table
        self.text: Optional[str] = text
        self.proxy: Optional[ProxyPlugin] = proxy
        self.browser: Optional[WebDriver] = browser
        self.appium: Optional[AppiumService] = appium
        self.appium_utils: Optional[AppiumUtils] = appium_utils
