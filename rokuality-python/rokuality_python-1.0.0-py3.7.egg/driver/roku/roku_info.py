import copy
from src.exceptions.server_failure_exception import ServerFailureException
from src.driver.roku.roku_device_info import RokuDeviceInfo

class RokuInfo():
    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Gets info about the Roku device under test such as version, power mode, etc.
	
	:returns: RokuDeviceInfo - Various information about the device under test.
	"""
    def get_device_info(self):
        session = copy.deepcopy(self.session)
        session['action'] = 'device_info'
        device_info_json = self.__handler(self.http_client.post_to_server('info', session))
        return RokuDeviceInfo(device_info_json)

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise ServerFailureException(element_json['results'])
        return element_json
