
import copy
from src.exceptions.remote_interact_exception import RemoteInteractException

class HDMIRemote():
    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Sends a remote control command to the device.
	
	:param button: - String - The button you wish to press on the device.
	
	:raises RemoteInteractException: If the remote button could not be pressed.
	"""
    def press_button(self, button):
        session = copy.deepcopy(self.session)
        session['action'] = 'press_button'
        session['remote_button'] = button
        self.__handler(self.http_client.post_to_server('remote', session))

    """
	Gets the available button commands for the device.
	
	:returns: - String - The available buttons for the device.
	
	:raises RemoteInteractException: If the list of buttons cannot be obtained.
	"""
    def get_button_options(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'get_buttons'
        json_results = self.__handler(self.http_client.post_to_server('remote', session))
        return json_results['button_options']

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise RemoteInteractException(element_json['results'])
        return element_json
