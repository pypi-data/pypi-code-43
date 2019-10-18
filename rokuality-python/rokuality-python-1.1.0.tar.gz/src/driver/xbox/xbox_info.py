import copy
from src.exceptions.server_failure_exception import ServerFailureException
from src.driver.xbox.xbox_device_info import XBoxDeviceInfo

class XBoxInfo():
    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Gets info about the XBox device under test such as os version, device id, etc.
	 
	:returns: XBoxDeviceInfo - Various information about the device under test.
	"""
    def get_device_info(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'device_info'
        device_info_json = self.__handler(self.http_client.post_to_server('info', session))
        return XBoxDeviceInfo(device_info_json)

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise ServerFailureException(element_json['results'])
        return element_json
