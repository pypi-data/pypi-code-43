import copy
from src.exceptions.server_failure_exception import ServerFailureException

class Options:

    session = None
    http_client = None

    def __init__(self, http_client, session):
        self.session = session
        self.http_client = http_client
    
    """
	Overrides the default Image Match Similarity value for all Image based elements. It will last for the duration
	of the driver session, or until a new value is set. A lower value 
	will increase the likelihood that your image locator will find a match, but too low a value
	and you can introduce false positives.
	
	:param image_match_similarity: float - the image match similarity to apply to all image elements i.e. '0.95'
	:raises ServerFailureException: If the image match similarity cannot be applied.
	"""
    def set_image_match_similarity(self, image_match_similarity):
        session = copy.deepcopy(self.session)
        session['action'] = 'image_match_similarity'
        session['image_match_similarity'] = str(image_match_similarity)
        element_json = self.__handler(self.http_client.post_to_server('settings', session))

    """
	Sets an implicit wait for all elements in milliseconds. It will last for the duration
	of the driver session, or until a new value is set. By default, when performing a finder().findElement
	command, the locator find will be evaluated immediately and throw an exception if the element is not immediately found.
	By setting this value, the server will search for the element repeatedly until the element is found, or will throw
	the NoSuchElementException if the element is not found after the duration expires. Setting this timeout is recommended
	but setting too high a value can result in increased test time.
	
	:param timeout_in_milliseconds: long - the timeout in milliseconds to wait for an element before throwing an exception.
	:raises ServerFailureException: If the timeout cannot be applied.
	"""
    def set_element_timeout(self, timeout_in_milliseconds):
        session = copy.deepcopy(self.session)
        session['action'] = 'element_find_timeout'
        session['element_find_timeout'] = str(timeout_in_milliseconds)
        element_json = self.__handler(self.http_client.post_to_server('settings', session))

    """
	Sets a poll interval for all elements in milliseconds. It will last for the duration
	of the driver session, or until a new value is set. Only applicable if an element timeout has been applied. By
	default the element poll interval is 250 milliseconds.
	
    :param poll_interval_in_milliseconds: long - the poll interval in milliseconds.
	:raises ServerFailureException: If the poll interval cannot be applied.
	"""
    def set_element_poll_interval(self, poll_interval_in_milliseconds):
        session = copy.deepcopy(self.session)
        session['action'] = 'element_polling_interval'
        session['element_polling_interval'] = str(poll_interval_in_milliseconds)
        element_json = self.__handler(self.http_client.post_to_server('settings', session))

    def __handler(self, element_json):
        if element_json['results'] != 'success':
            raise ServerFailureException(element_json['results'])
        return element_json

