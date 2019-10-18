
import copy
from src.exceptions.remote_interact_exception import RemoteInteractException
from src.enums.roku_button import RokuButton

class RokuRemote():
    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Sends a remote control command to the device.
	
	:param button: - The button you wish to press on the device.
	
	:raises RemoteInteractException: If the remote button could not be pressed.
	"""
    def press_button(self, button):
        session = copy.deepcopy(self.session)
        session['action'] = 'press_button'
        session['remote_button'] = button.value
        self.__handler(self.http_client.post_to_server('remote', session))

    """
	Sends a literal string of text to the device. Only relevant if you are interacting with a Roku text input.

	:param text_to_type String - The text you wish to type into the input field.
	
	:raises RemoteInteractException: If the input fails to be sent.
	"""
    def send_keys(self, text_to_type):
        session = copy.deepcopy(self.session)
        session['action'] = 'send_keys'
        session['text'] = text_to_type
        self.__handler(self.http_client.post_to_server('remote', session))

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise RemoteInteractException(element_json['results'])
        return element_json
