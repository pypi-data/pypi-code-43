
import copy
from src.utils.file_to_string_utils import FileToStringUtils
from src.driver.element import Element
from src.driver.by import By
from src.exceptions.no_such_element_exception import NoSuchElementException

class Finder:

    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Searches for the existence of a locator within the device screen.
	
	:param by: The locator to search for.
	:returns: Element - An Element object containing details about the elements location and contents.
	:raises NoSuchElementException: If the locator can not be found on the screen.
	"""
    def find_element(self, by):
        by = FileToStringUtils().prepare_locator(by)
        session = copy.deepcopy(self.session)
        session['action'] = 'find'
        session['element_locator'] = str(by)
        element_json = self.__handler(self.http_client.post_to_server('element', session))
        return Element(element_json)

    """
	Searches for the existence of a locator within the device sub screen starting at
	subScreenX, subScreenY, and with subScreenWidth and subScreenHeight.

	:param by: The locator to search for in the device subscreen.
	:param sub_screen_x: int - The x coordinate starting point of the subscreen.
	:param sub_screen_y: int - The y coordinate starting point of the subscreen.
	:param sub_screen_width: int - The subscreen width ending point.
	:param sub_screen_height: int - The subscreen height ending point.

	:returns: Element - An Element object containing details about the elements location and contents.
	:raises NoSuchElementException: If the locator can not be found on the screen.
	"""
    def find_element_sub_screen(self, by, sub_screen_x, sub_screen_y, sub_screen_width, sub_screen_height):
        by = FileToStringUtils().prepare_locator(by)
        session = copy.deepcopy(self.session)
        session['action'] = 'find'
        session['element_locator'] = str(by)
        session['sub_screen_x'] = int(sub_screen_x)
        session['sub_screen_y'] = int(sub_screen_y)
        session['sub_screen_width'] = int(sub_screen_width)
        session['sub_screen_height'] = int(sub_screen_height)
        element_json = self.__handler(self.http_client.post_to_server('element', session))
        return Element(element_json)

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise NoSuchElementException(element_json['results'])
        return element_json

