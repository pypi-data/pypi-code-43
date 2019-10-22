import pprint

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

# def create_function(orgin_func,name, args):
#     def y():
#         print("s")
#         orgin_func(args)
#         pass
#
#
#     y_code = types.CodeType(orgin_func.__code__.co_argcount,
#                             orgin_func.__code__.co_kwonlyargcount,
#                             orgin_func.__code__.co_nlocals,
#                             orgin_func.__code__.co_stacksize,
#                             orgin_func.__code__.co_flags,
#                             y.__code__.co_code,
#                             orgin_func.__code__.co_consts,
#                             orgin_func.__code__.co_names,
#                             orgin_func.__code__.co_varnames,
#                             y.__code__.co_filename,
#                             name,
#                             y.__code__.co_firstlineno,
#                             y.__code__.co_lnotab)
#
#     return types.FunctionType(y_code, orgin_func.__globals__, name)
from shield34_reporter.auth.sdk_authentication import SdkAuthentication
from shield34_reporter.container.run_report_container import RunReportContainer
from shield34_reporter.model.csv_rows.actions.action_click_and_hold_csv_row import ActionClickAndHoldCsvRow, \
    ActionClickAndHoldElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_click_csv_row import ActionClickCsvRow, ActionClickElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_context_click_csv_row import ActionContextClickCsvRow, \
    ActionContextClickElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_double_click_csv_row import ActionDoubleClickCsvRow, ActionDoubleClickElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_drag_and_drop_element_by_offset import ActionDragAndDropElementByOffset
from shield34_reporter.model.csv_rows.actions.action_drag_and_drop_element_to_element_csv_row import \
    ActionDragAndDropElementToElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_key_down_csv_row import ActionKeyDownCsvRow, ActionKeyDownElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_key_up_csv_row import ActionKeyUpCsvRow, ActionKeyUpElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_move_by_offset_csv_row import ActionMoveByOffsetCsvRow
from shield34_reporter.model.csv_rows.actions.action_move_to_element_csv_row import ActionMoveToElementCsvRow
from shield34_reporter.model.csv_rows.actions.action_move_to_element_with_offset_csv_row import ActionMoveToElementWithOffsetCsvRow
from shield34_reporter.model.csv_rows.actions.action_send_keys_csv_row import ActionSendKeysCsvRow, ActionSendKeysWithElementCsvRow
from shield34_reporter.model.csv_rows.exception_caught_csv_row import ExceptionCaughtCsvRow
from shield34_reporter.model.csv_rows.helpers.exception_desc import ExceptionDesc
from shield34_reporter.model.csv_rows.html.PageHtmlCsvRow import PageHtml
from shield34_reporter.model.csv_rows.html.WebElementHtmlCsvRow import WebElementHtml
from shield34_reporter.model.csv_rows.step_failed_csv_row import StepFailedCsvRow
from shield34_reporter.model.csv_rows.test_action.action_ended_csv_row import ActionEndedCsvRow
from shield34_reporter.model.csv_rows.test_action.action_started_csv_row import ActionStartedCsvRow
from shield34_reporter.model.csv_rows.web_driver.web_driver_close_csv_row import WebDriverCloseCsvRow
from shield34_reporter.model.csv_rows.web_driver.web_driver_find_element_csv_row import WebDriverFindElementCsvRow
from shield34_reporter.model.csv_rows.web_driver.web_driver_find_elements_csv_row import WebDriverFindElementsCsvRow
from shield34_reporter.model.csv_rows.web_driver.web_driver_get_csv_row import WebDriverGetCsvRow
from shield34_reporter.model.csv_rows.web_driver.web_driver_quit_csv_row import WebDriverQuitCsvRow
from shield34_reporter.model.csv_rows.web_element.web_element_clear_csv_row import WebElementClearCsvRow
from shield34_reporter.model.csv_rows.web_element.web_element_click_csv_row import WebElementClickCsvRow
from shield34_reporter.model.csv_rows.web_element.web_element_find_element_csv_row import WebElementFindElementCsvRow
from shield34_reporter.model.csv_rows.web_element.web_element_find_elements_csv_row import WebElementFindElementsCsvRow
from shield34_reporter.model.csv_rows.web_element.web_element_send_keys_csv_row import WebElementSendKeysCsvRow
from shield34_reporter.model.enums.action_name import ActionName
from shield34_reporter.model.enums.exception_type import ExceptionType
from shield34_reporter.model.enums.placement import Placement
from shield34_reporter.utils.driver_utils import DriverUtils
from shield34_reporter.utils.reporter_proxy import ReporterProxy
from shield34_reporter.utils.screen_shots import ScreenShot
from shield34_reporter.utils.web_element_utils import WebElementUtils


class SeleniumOverrider():
    is_overrided= False



    @staticmethod
    def override():
        if not SeleniumOverrider.is_overrided and SdkAuthentication.isAuthorized:
            WebElementOverrider.override()
            WebDriverOverrider.override()
            ActionsOverrider.override()
            SeleniumOverrider.is_overrided = True

    @staticmethod
    def finalize_failed_action(exception, action_name):
        RunReportContainer.add_report_csv_row(ExceptionCaughtCsvRow(exception, ExceptionType.MAIN_ACTION))
        ScreenShot.capture_screen_shoot(action_name.value, Placement.AFTER_FAILURE.value)
        RunReportContainer.add_report_csv_row(StepFailedCsvRow(ExceptionDesc(exception).message))


class WebElementOverrider():

    @staticmethod
    def override():
        WebElement.org_find_elements = WebElement.find_elements

        def element_find_elements(obj, by, value):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebElementFindElementsCsvRow(obj, DriverUtils.get_current_driver(), by + ": " + value))
            try:
                res = WebElement.org_find_elements(obj, by, value)
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                for elem in res:
                    RunReportContainer.get_current_block_run_holder().add_web_element(elem.id, by + ": " + value)
            except Exception as e:
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_ELEMENT_FIND_ELEMENTS)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return res

        WebElement.find_elements = element_find_elements

        WebElement.org_find_element = WebElement.find_element

        def element_find_element(obj, by, value):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebElementFindElementCsvRow(obj, DriverUtils.get_current_driver(), by + ": " + value))
            try:
                res = WebElement.org_find_element(obj, by, value)
                RunReportContainer.add_report_csv_row(WebElementHtml(WebElementUtils.get_element_html(res),
                    WebElementUtils.get_element_computed_css(res, DriverUtils.get_current_driver()),
                    WebElementUtils.get_element_wrapping_html(res, 3)))
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                RunReportContainer.get_current_block_run_holder().add_web_element(res.id, by + ": " + value)
            except Exception as e:
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_ELEMENT_FIND_ELEMENT)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return res

        WebElement.find_element = element_find_element

        WebElement.org_click = WebElement.click

        def click_element(obj):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebElementClickCsvRow(obj, DriverUtils.get_current_driver()))
            try:
                WebElement.org_click(obj)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_ELEMENT_CLICK)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())

        WebElement.click = click_element

        WebElement.org_send_keys = WebElement.send_keys

        def send_keys_to_element(obj, *value):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebElementSendKeysCsvRow(obj, DriverUtils.get_current_driver(), *value))
            try:
                WebElement.org_send_keys(obj, *value)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_ELEMENT_SEND_KEYS)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())

        WebElement.send_keys = send_keys_to_element

        WebElement.org_element_clear = WebElement.clear

        def element_clear(obj):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebElementClearCsvRow(obj, DriverUtils.get_current_driver()))
            try:
                WebElement.org_element_clear(obj)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_ELEMENT_CLEAR)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())

        WebElement.clear = element_clear


class WebDriverOverrider():
    @staticmethod
    def override():

        WebDriver.org_init = WebDriver.__init__

        def init_web_driver(self, command_executor='http://127.0.0.1:4444/wd/hub',
                 desired_capabilities=None, browser_profile=None, proxy=None,
                 keep_alive=False, file_detector=None, options=None):
            updated_desired_capabilities = desired_capabilities
            if SdkAuthentication.is_authorized():
                if updated_desired_capabilities is None:
                    updated_desired_capabilities = {}
                updated_desired_capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}
                updated_desired_capabilities['acceptInsecureCerts'] = True

                if ReporterProxy.create_proxy():
                    options = webdriver.ChromeOptions()
                    RunReportContainer.get_current_block_run_holder().proxyServer.add_to_capabilities(updated_desired_capabilities)
            WebDriver.org_init(self, command_executor, updated_desired_capabilities, browser_profile, proxy, keep_alive, file_detector, options)

        WebDriver.__init__ = init_web_driver

        WebDriver.org_find_elements = WebDriver.find_elements

        def shield_find_elements(obj, by, value):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebDriverFindElementsCsvRow(DriverUtils.get_current_driver(), by + ": " + value))
            try:
                res = WebDriver.org_find_elements(obj, by, value)
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                for elem in res:
                    RunReportContainer.get_current_block_run_holder().add_web_element(elem.id, by + ": " + value)
            except Exception as e:
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_DRIVER_FIND_ELEMENTS)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return res

        WebDriver.find_elements = shield_find_elements

        WebDriver.org_find_element = WebDriver.find_element

        def shield_find_element(obj, by, value):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebDriverFindElementCsvRow(DriverUtils.get_current_driver(), by + ": " + value))
            try:
                res = WebDriver.org_find_element(obj, by, value)
                RunReportContainer.add_report_csv_row(WebElementHtml(WebElementUtils.get_element_html(res),
                                                                     WebElementUtils.get_element_computed_css(res,
                                                                                                              DriverUtils.get_current_driver()),
                                                                     WebElementUtils.get_element_wrapping_html(res, 3)))
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                RunReportContainer.get_current_block_run_holder().add_web_element(res.id, by + ": " + value)
            except Exception as e:
                RunReportContainer.add_report_csv_row(PageHtml(DriverUtils.get_page_html()))
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_DRIVER_FIND_ELEMENT)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return res

        WebDriver.find_element = shield_find_element

        WebDriver.org_get = WebDriver.get

        def get_url(obj, url):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.get_current_block_run_holder().proxyServer.new_har("shield34.com", options={'captureHeaders': True, 'captureContent': True, 'captureCookies': True, 'captureBinaryContent': True, 'initialPageRef': True, 'initialPageTitle': True})
            try:
                current_driver = DriverUtils.get_current_driver()
                RunReportContainer.add_report_csv_row(WebDriverGetCsvRow(current_driver, url))
                WebDriver.org_get(obj, url)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_DRIVER_GET)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())

        WebDriver.get = get_url

        WebDriver.org_quit = WebDriver.quit

        def web_driver_quit(obj):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebDriverQuitCsvRow(DriverUtils.get_current_driver()))
            try:
                WebDriver.org_quit(obj)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_DRIVER_QUIT)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())

        WebDriver.quit = web_driver_quit

        WebDriver.org_close = WebDriver.close

        def web_driver_close(obj):
            RunReportContainer.get_current_block_run_holder().proxyServer.har
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(WebDriverCloseCsvRow(DriverUtils.get_current_driver()))
            try:
                WebDriver.org_close(obj)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.WEB_DRIVER_CLOSE)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())

        WebDriver.close = web_driver_close


class ActionsOverrider():

    @staticmethod
    def override():
        ActionChains.org_click = ActionChains.click

        def action_click(obj, on_element=None):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            if on_element is None:
                RunReportContainer.add_report_csv_row(ActionClickCsvRow(DriverUtils.get_current_driver()))
                action_name = ActionName.ACTION_CLICK
            else:
                RunReportContainer.add_report_csv_row(ActionClickElementCsvRow(DriverUtils.get_current_driver(), on_element))
                action_name = ActionName.ACTION_CLICK_ELEMENT
            try:
                actions = ActionChains.org_click(obj, on_element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, action_name)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.click = action_click

        ActionChains.org_click_and_hold = ActionChains.click_and_hold

        def action_click_and_hold(obj, on_element=None):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())

            if on_element is None:
                RunReportContainer.add_report_csv_row(ActionClickAndHoldCsvRow(DriverUtils.get_current_driver()))
                action_name = ActionName.ACTION_CLICK_AND_HOLD
            else:
                RunReportContainer.add_report_csv_row(ActionClickAndHoldElementCsvRow(DriverUtils.get_current_driver(), on_element))
                action_name = ActionName.ACTION_WEB_ELEMENT_CLICK_AND_HOLD
            try:
                actions = ActionChains.org_click_and_hold(obj, on_element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, action_name)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.click_and_hold = action_click_and_hold

        ActionChains.org_context_click = ActionChains.context_click

        def action_context_clock(obj, on_element=None):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            if on_element is None:
                RunReportContainer.add_report_csv_row(ActionContextClickCsvRow(DriverUtils.get_current_driver()))
                action_name = ActionName.ACTION_CONTEXT_CLICK
            else:
                RunReportContainer.add_report_csv_row(ActionContextClickElementCsvRow(DriverUtils.get_current_driver(), on_element))
                action_name = ActionName.ACTION_WEB_ELEMENT_CONTEXT_CLICK
            try:
                actions = ActionChains.org_context_click(obj, on_element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, action_name)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.context_click = action_context_clock

        ActionChains.org_double_click = ActionChains.double_click

        def action_double_click(obj, on_element=None):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            if on_element is None:
                RunReportContainer.add_report_csv_row(ActionDoubleClickCsvRow(DriverUtils.get_current_driver()))
                action_name = ActionName.ACTION_DOUBLE_CLICK
            else:
                RunReportContainer.add_report_csv_row(ActionDoubleClickElementCsvRow(DriverUtils.get_current_driver(), on_element))
                action_name = ActionName.ACTION_WEB_ELEMENT_DOUBLE_CLICK
            try:
                actions = ActionChains.org_double_click(obj, on_element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, action_name)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.double_click = action_double_click

        ActionChains.org_drag_and_drop_by_offset = ActionChains.drag_and_drop_by_offset

        def action_drag_and_drop_by_offset(obj, source, xoffset, yoffset):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(ActionDragAndDropElementByOffset(DriverUtils.get_current_driver(), source, xoffset, yoffset))
            try:
                actions = ActionChains.org_drag_and_drop_by_offset(obj, source, xoffset, yoffset)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_DRAG_AND_DROP_ELEMENT_BY_OFFSET)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions
        ActionChains.drag_and_drop_by_offset = action_drag_and_drop_by_offset

        ActionChains.org_drag_and_drop = ActionChains.drag_and_drop

        def action_drag_and_drop(obj, source, target):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(ActionDragAndDropElementToElementCsvRow(DriverUtils.get_current_driver(), source, target))
            try:
                actions = ActionChains.org_drag_and_drop(obj, source, target)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_DRAG_AND_DROP_ELEMENT_TO_ELEMENT)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.drag_and_drop = action_drag_and_drop

        ActionChains.org_key_down = ActionChains.key_down

        def action_key_down(obj, value, element=None):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            if element is None:
                RunReportContainer.add_report_csv_row(ActionKeyDownCsvRow(DriverUtils.get_current_driver(), value))
                action_name = ActionName.ACTION_KEY_DOWN
            else:
                RunReportContainer.add_report_csv_row(ActionKeyDownElementCsvRow(DriverUtils.get_current_driver(), element, value))
                action_name = ActionName.ACTION_KEY_DOWN_ELEMENT
            try:
                actions = ActionChains.org_key_down(obj, value, element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, action_name)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.key_down = action_key_down

        ActionChains.org_key_up = ActionChains.key_up

        def action_key_up(obj, value, element=None):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            if element is None:
                RunReportContainer.add_report_csv_row(ActionKeyUpCsvRow(DriverUtils.get_current_driver(), value))
                action_name = ActionName.ACTION_KEY_UP
            else:
                RunReportContainer.add_report_csv_row(
                    ActionKeyUpElementCsvRow(DriverUtils.get_current_driver(), element, value))
                action_name = ActionName.ACTION_WEB_ELEMENT_KEY_UP
            try:
                actions = ActionChains.org_key_up(obj, value, element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, action_name)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.key_up = action_key_up

        ActionChains.org_move_by_offset = ActionChains.move_by_offset

        def action_move_by_offset(obj, xoffset, yoffset):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(ActionMoveByOffsetCsvRow(DriverUtils.get_current_driver(), xoffset, yoffset))
            try:
                actions = ActionChains.org_move_by_offset(obj, xoffset, yoffset)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_MOVE_BY_OFFSET)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.move_by_offset = action_move_by_offset

        ActionChains.org_send_keys = ActionChains.send_keys

        def action_send_keys(obj, *keys_to_send):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(
                ActionSendKeysCsvRow(DriverUtils.get_current_driver(), *keys_to_send))
            try:
                actions = ActionChains.org_send_keys(obj, *keys_to_send)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_SEND_KEYS)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.send_keys = action_send_keys

        ActionChains.org_send_keys_to_element = ActionChains.send_keys_to_element

        def action_send_keys_to_element(obj, element, *keys_to_send):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(
                ActionSendKeysWithElementCsvRow(DriverUtils.get_current_driver(), element, *keys_to_send))
            try:
                actions = ActionChains.org_send_keys_to_element(obj, element, *keys_to_send)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_SEND_KEYS_ELEMENT)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.send_keys_to_element = action_send_keys_to_element

        ActionChains.org_move_to_element = ActionChains.move_to_element

        def action_move_to_element(obj, to_element):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(
                ActionMoveToElementCsvRow(DriverUtils.get_current_driver(), to_element))
            try:
                actions = ActionChains.org_move_to_element(obj, to_element)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_MOVE_TO_ELEMENT)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.move_to_element = action_move_to_element

        ActionChains.org_move_to_element_with_offset = ActionChains.move_to_element_with_offset

        def action_move_to_element_with_offset(obj, to_element, xoffset, yoffset):
            RunReportContainer.add_report_csv_row(ActionStartedCsvRow())
            RunReportContainer.add_report_csv_row(
                ActionMoveToElementWithOffsetCsvRow(DriverUtils.get_current_driver(), to_element, xoffset, yoffset))
            try:
                actions = ActionChains.org_move_to_element_with_offset(obj, to_element, xoffset, yoffset)
            except Exception as e:
                SeleniumOverrider.finalize_failed_action(e, ActionName.ACTION_MOVE_TO_ELEMENT_WITH_OFFSET)
                raise e
            finally:
                RunReportContainer.add_report_csv_row(ActionEndedCsvRow())
            return actions

        ActionChains.move_to_element_with_offset = action_move_to_element_with_offset




