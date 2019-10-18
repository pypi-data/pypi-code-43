
class Element:

    element_y = None
    element_x = None
    element_width = None
    element_height = None
    element_confidence = None
    element_text = None
    session_id = None
    element_id = None

    def __init__(self, element_json):
        self.element_x = element_json["element_x"]
        self.element_y = element_json["element_y"]
        self.element_width = int(element_json["element_width"])
        self.element_height = int(element_json["element_height"])
        self.element_confidence = element_json["element_confidence"]
        self.element_text = element_json["element_text"]
        self.session_id = element_json["session_id"]
        self.element_id = element_json["element_id"]

    """
	Gets the session id that the element belongs to.
	
	:returns: String - the session id
	"""
    def get_session_id(self):
        return self.session_id

    """
	Gets the element id.
	
	:returns: String - the element id
	"""
    def get_element_id(self):
        return self.element_id

    """
	Gets the text of the element. If an image based 
    locator it will be any found text within the matched element.
	
	:returns: String - the text of the element
	"""
    def get_text(self):
        return self.element_text

    """
	Gets the width of the element.
	
	:returns: int - the width of the element
	"""
    def get_width(self):
        return self.element_width

    """
	Gets the height of the element.
	
	:returns: int - the height of the element
	"""
    def get_height(self):
        return self.element_height

    """
	Gets the starting x of the element.
	
	:returns: int - the starting x position of the element
	"""
    def get_x(self):
        return self.element_x

    """
	Gets the starting y of the element.

	:returns: int - the starting x position of the element
	"""
    def get_y(self):
        return self.element_y

    """
	Gets the confidence score of the element match.
	
	:returns: float - the confidence of the match
	"""
    def get_confidence(self):
        return self.element_confidence