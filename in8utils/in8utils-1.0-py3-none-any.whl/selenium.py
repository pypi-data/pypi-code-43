import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as BaseWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def wait_for_element_to_be_present(driver: BaseWebDriver, by: By, selector: str, seconds=240) -> bool:
    try:
        wait_until(
            driver,
            selector,
            by,
            seconds,
            EC.presence_of_element_located
        )
        return True
    except Exception as ex:
        import traceback
        traceback.print_exc()
        print("Element was not loaded: {}".format(ex))
        return False


def wait_until_invisibility(driver: BaseWebDriver, by: By, selector: str, seconds=240) -> bool:
    try:
        wait_until(
            driver,
            selector,
            by,
            seconds,
            EC.invisibility_of_element_located,
        )
        return True
    except Exception as ex:
        print("Element did not become invisible: {}".format(ex))
        return False


def wait_for_element_to_be_visible(driver: BaseWebDriver, by: By, selector: str, seconds=240) -> bool:
    try:
        wait_until(
            driver,
            selector,
            by,
            seconds,
            EC.visibility_of_element_located
        )
        return True
    except Exception as ex:
        print("Element did not become visible: {}".format(ex))
        return False


def wait_until(driver: BaseWebDriver, selector: str, by: By, seconds: int, expected_condition) -> None:
    WebDriverWait(driver, seconds).until(
        expected_condition((by, selector))
    )


def scroll_to(driver: BaseWebDriver, element: WebElement, x=0, y=0):
    time.sleep(0.5)

    # Scroll to limit of element.
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

    if x != 0 or y != 0:
        driver.execute_script("window.scrollBy({},{})".format(x, y))

    time.sleep(0.5)


def remove_element(driver: BaseWebDriver, css_selector: str) -> None:
    el = driver.find_element_by_css_selector(css_selector)
    driver.execute_script("arguments[0].remove();", el)


def remove_all_elements(driver: BaseWebDriver, css_selector: str) -> None:
    driver.execute_script(
        "document.querySelectorAll(\"{}\").forEach((item, index) => item.remove());".format(css_selector))
