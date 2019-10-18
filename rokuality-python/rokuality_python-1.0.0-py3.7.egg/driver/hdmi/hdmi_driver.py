
from src.httpexecutor.http_client import HttpClient
from src.driver.device_capabilities import DeviceCapabilities
from src.driver.base_driver import BaseDriver
from src.driver.finder import Finder
from src.exceptions.session_not_started_exception import SessionNotStartedException
from src.driver.options import Options
from src.driver.hdmi.hdmi_remote import HDMIRemote
from src.driver.screen import Screen

class HDMIDriver(BaseDriver):
    pass

    http_client = None

    """
	Starts a new hdmi driver session (Playstation, Cable SetTop Box, AppleTV, AndroidTV, etc).
	
	:param server_url: String - The url your server is listening at, i.e. http://localhost:port
	:param capabilities: DeviceCapabilities - The capabilities for your driver session.
	
	:raises SessionNotStartedException: If a session could not be initiated.
	"""
    def __init__(self, server_url, capabilities : DeviceCapabilities):
        self.http_client = HttpClient(server_url)
        super().set_server_url(server_url)
        cap_json = capabilities.get_capabilities_as_json()
        cap_json = super().prepare_cap_json(cap_json)
        cap_json['action'] = 'start'
        session_json = self.__handler(self.http_client.post_to_server('session', cap_json))
        super().set_session(session_json)
    
    """
	Stops the hdmi driver session and releases all assets. Should be called as the last command of every session.
	
	:raises ServerFailureException: If a session could not be properly torn down for any reason.
	"""
    def stop(self):
        session = super().get_session()
        session['action'] = 'stop'
        if not super().get_session() is None:
            self.__handler(self.http_client.post_to_server('session', session))

    """
	Initiates the Finder for finding elements.
	 
	:returns: Finder
	"""
    def finder(self):
        return Finder(self.http_client, super().get_session())

    """
	Initiates the HDMI Remote for sending remote control commands.
	
	:returns: HDMIRemote
	"""
    def remote(self):
        return HDMIRemote(self.http_client, super().get_session())

    """
	Initiates the Screen for getting information and artifacts from the device screen.
	
	:returns: Screen
	"""
    def screen(self):
        return Screen(self.http_client, super().get_session())

    """
	Initiates Options for various driver and finder settings.
	
	:returns: Options
	"""
    def options(self):
        return Options(self.http_client, super().get_session())

    """
	Gets the session id of the device under test.
	
	:returns: String
	"""
    def get_session_id(self):
        return super().get_session()['session_id']

    def __handler(self, session_json):
        if session_json['results'] != 'success':
            raise SessionNotStartedException(session_json['results'])
        return session_json

