from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


def get_locator_search(name=None, identifier=None, xpath=None, css=None, contains=None):
    if name is None and identifier is None and xpath is None and css is None and contains is None:
        raise ValueError

    if name is not None:
        return By.NAME, name
    if identifier is not None:
        return By.ID, identifier
    if xpath is not None:
        return By.XPATH, xpath
    if css is not None:
        return By.CSS_SELECTOR, css
    if contains is not None:
        return By.PARTIAL_LINK_TEXT, contains


def find_element(driver, name=None, identifier=None, xpath=None, css=None, contains=None):
    r"""Return an element from a description of the component.

    Returns an element searching on all html filtering by its name, id,
    xpath expression or css selector. It returns the first match that
    the descriptions get from the code.

    Args:
        driver (WebDriver): WebDriver that hosts the main web to find.
        name (string): name value of the html element
        identifier (string): id value of the html element
        xpath (string): xpath expression that describes the element
        css (string): css selector that describes the element
    Returns:
        WebElement: First element that matches the description.
    """

    by, value = get_locator_search(name, identifier, xpath, css, contains)
    return driver.find_element(by, value)


def find_elements(driver, name=None, identifier=None, xpath=None, css=None, contains=None):
    r"""Return an element from a description of the component.

    Returns some elements searching on all html filtering by its name, id,
    xpath expression or css selector. It returns all the matches that
    the descriptions get from the code.

    Args:
        driver (WebDriver): WebDriver that hosts the main web to find.
        name (string): name value of the html element
        identifier (string): id value of the html element
        xpath (string): xpath expression that describes the element
        css (string): css selector that describes the element
    Returns:
        WebElement: First element that matches the description.
    """

    by, value = get_locator_search(name, identifier, xpath, css, contains)
    return driver.find_elements(by, value)


def fill_input(driver, text, name=None, identifier=None, xpath=None, css=None, contains=None):
    elem = find_element(driver, name, identifier, xpath, css, contains)
    elem.clear()
    elem.send_keys(text)


def fill_select(driver, text, name=None, identifier=None, xpath=None, css=None, contains=None):
    elem = Select(find_element(driver, name, identifier, xpath, css, contains))
    elem.select_by_visible_text(text)


def key_intro(driver, name=None, identifier=None, xpath=None, css=None, contains=None):
    elem = find_element(driver, name, identifier, xpath, css, contains)
    elem.send_keys(Keys.RETURN)


def click(driver, name=None, identifier=None, xpath=None, css=None, contains=None):
    elem = find_element(driver, name, identifier, xpath, css, contains)
    elem.click()


def get_child_tags(element, tag="*"):
    return element.find_elements_by_xpath(".//" + tag)


def remove_element(driver, css):
    driver.execute_script(f"""
        var element = document.querySelector("{css}");
        if (element)
            element.parentNode.removeChild(element);
        """)

def wait_until_loaded(driver, name=None, identifier=None, xpath=None, css=None, contains=None, delay=10):
    loctype, search = get_locator_search(name, identifier, xpath, css, contains)
    WebDriverWait(driver, delay).until(ec.presence_of_element_located((loctype, search)))


def wait_until_alert(driver):
    WebDriverWait(driver, 100).until(ec.alert_is_present())