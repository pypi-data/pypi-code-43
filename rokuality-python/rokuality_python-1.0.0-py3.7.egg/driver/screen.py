import json
import copy
from src.exceptions.screen_exception import ScreenException
from src.utils.file_to_string_utils import FileToStringUtils
from src.driver.screen_text import ScreenText
from src.driver.screen_size import ScreenSize

class Screen:

    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Gets the device screen image and saves it to a temporary file on your machine.
	
	:returns: Path to the saved file of the device screen image at the time of capture.
	:raises ScreenException: If the device screen fails to capture.
	"""
    def get_image(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_screen_image'
        screen_json = self.__handler(self.http_client.post_to_server('screen', session))
        return FileToStringUtils().convert_to_file(screen_json["screen_image"], screen_json["screen_image_extension"])

    """
	Gets the device sub screen image and saves it to a temporary file on your machine.
	
	:param sub_screen_x: int - The x coordinate starting point of the subscreen to capture.
	:param sub_screen_y: int - The y coordinate starting point of the subscreen to capture.
	:param sub_screen_width: int - The subscreen width ending point to capture.
	:param sub_screen_height: - int The subscreen height ending point to capture.
	
	:returns: Path to the saved file of the device sub screen image at the time of capture.
	:raises ScreenException: If the device sub screen fails to capture.
	"""
    def get_image_sub_screen(self, sub_screen_x, sub_screen_y, sub_screen_width, sub_screen_height):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_screen_image'
        session['sub_screen_x'] = int(sub_screen_x)
        session['sub_screen_y'] = int(sub_screen_y)
        session['sub_screen_width'] = int(sub_screen_width)
        session['sub_screen_height'] = int(sub_screen_height)
        screen_json = self.__handler(self.http_client.post_to_server('screen', session))
        return FileToStringUtils().convert_to_file(screen_json["screen_image"], screen_json["screen_image_extension"])

    """
	Gets the device screen text as a ScreenText collection with details about each found word on the screen.
	
	:returns: ScreenText - A collection of ScreenText objects containing details of every found word on the device screen.
	:raises ScreenException: If the device screen text fails to capture.
	"""
    def get_text(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_screen_text'
        screen_json = self.__handler(self.http_client.post_to_server('screen', session))
        return self.__get_screen_texts(screen_json)

    """
	Gets the device screen text from the identified device sub screen as a ScreenText 
	collection with details about each found word on the screen.
	
	:param sub_screen_x: int - The x coordinate starting point of the subscreen to capture.
	:param sub_screen_y: int - The y coordinate starting point of the subscreen to capture.
	:param sub_screen_width: int - The subscreen width ending point to capture.
	:param sub_screen_height: - int The subscreen height ending point to capture.

	:returns: ScreenText - A collection of ScreenText objects containing details of every found word on the device sub screen.
	:raises ScreenException: If the device sub screen text fails to capture.
	"""
    def get_text_sub_screen(self, sub_screen_x, sub_screen_y, sub_screen_width, sub_screen_height):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_screen_text'
        session['sub_screen_x'] = int(sub_screen_x)
        session['sub_screen_y'] = int(sub_screen_y)
        session['sub_screen_width'] = int(sub_screen_width)
        session['sub_screen_height'] = int(sub_screen_height)
        screen_json = self.__handler(self.http_client.post_to_server('screen', session))
        return self.__get_screen_texts(screen_json)

    """
	Gets the device screen text as a complete String.
	
	:returns: String - A complete string of every word found on the screen.
	:raises ScreenException: If the device screen text fails to capture.
	"""
    def get_text_as_string(self):
        screen_texts = self.get_text()
        constructed_screen_text = ""
        for screen_text in screen_texts:
            constructed_screen_text = constructed_screen_text + screen_text.get_text() + " "
        return constructed_screen_text

    """
	Gets the device sub screen text as a complete String.
	
	:param sub_screen_x: int - The x coordinate starting point of the subscreen to capture.
	:param sub_screen_y: int - The y coordinate starting point of the subscreen to capture.
	:param sub_screen_width: int - The subscreen width ending point to capture.
	:param sub_screen_height: - int The subscreen height ending point to capture.
	
	:returns: String - A complete string of every word found on the sub screen.
	:raises ScreenException: If the device screen text fails to capture.
	"""
    def get_text_as_string_sub_screen(self, sub_screen_x, sub_screen_y, sub_screen_width, sub_screen_height):
        screen_texts = self.get_text_sub_screen(sub_screen_x, sub_screen_y, sub_screen_width, sub_screen_height)
        constructed_screen_text = ""
        for screen_text in screen_texts:
            constructed_screen_text = constructed_screen_text + screen_text.get_text() + " "
        return constructed_screen_text

    """
	Gets the device screen size.
	
	:returns: ScreenSize - The size of the device under test.
	:raises ScreenException: If the device screen size is not determined.
	"""
    def get_screen_size(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_screen_size'
        screen_json = self.__handler(self.http_client.post_to_server('screen', session))
        return ScreenSize(screen_json)

    """
	Gets the device screen recording from the driver start to current. Note the recording is generated
	in .mp4 format but is done through stitching the collected device screenshots together from the
	start of the driver seesion - and the quality of the capture won't be the best. But very useful
	for reporting and debugging.

	:returns: Video - An .mp4 video of the driver session from start until current.
	:raises ScreenException: If the video recording cannot be captured.
	"""
    def get_recording(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_screen_recording'
        screen_json = self.__handler(self.http_client.post_to_server('screen', session))
        return FileToStringUtils().convert_to_file(screen_json["screen_video"], screen_json["screen_video_extension"])

    def __get_screen_texts(self, screen_json):
        screen_text_json = screen_json['screen_text']
        all_screen_text = []
        json_dict = json.loads(screen_text_json)
        i = 0
        count = len(json_dict)
        while i < count:
            value = json_dict[i]
            all_screen_text.append(ScreenText(value))
            i = i + 1
        return all_screen_text

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise ScreenException(element_json['results'])
        return element_json

