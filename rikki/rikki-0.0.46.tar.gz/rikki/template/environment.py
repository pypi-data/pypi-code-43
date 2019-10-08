
environment_template = """
from allure_behave.hooks import allure_report
from appium import webdriver
from appium.webdriver.appium_service import AppiumService
from behave.model import Scenario
from rikki.behave.context import Context


def before_all(ctx: Context):
    setattr(ctx, "appium", AppiumService())
    ctx.appium.start()
    setattr(ctx, "proxy", ctx.config.proxy)


def after_all(ctx: Context):
    ctx.proxy.shutdown()
    ctx.appium.stop()


def before_scenario(ctx: Context, scenario: Scenario):
    # start browser
    ctx.proxy.reset()
    #     Android capabilities
    #     desired_capabilities = {
    #         "platformName": "Android",
    #         "deviceName": None,
    #         "automationName": "uiautomator2",
    #         "appPackage": None,
    #         "appActivity": None,
    #         "noReset": "noReset" in scenario.tags,
    #         "app": None
    #     }
    #     iOS Capabilities
    #     desired_capabilities = {
    #         "platformName": "iOS",
    #         "deviceName": None,
    #         "platformVersion": None
    #         "automationName": "XCUITest",
    #         "noReset": "noReset" in scenario.tags,
    #         "app": None
    #     }
    #     Decide which utils to use
    #     setattr(ctx, "appium_utils", Choose From one of AppiumUtils subclasses)
    ctx.browser = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities)

    ctx.browser.implicitly_wait(10)


def after_scenario(ctx: Context, scenario: Scenario):
    ctx.browser.quit()
    ctx.proxy.reset()


allure_report("./reports")

"""
