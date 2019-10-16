
class ScreenText:

    text = None
    location_x = None
    location_y = None
    width = None
    height = None
    confidence = None

    def __init__(self, element_json):
        self.text = element_json["text"]
        location_json = element_json["location"]
        self.location_x = int(location_json["x"])
        self.location_y = int(location_json["y"])
        self.width = int(element_json["length"])
        self.height = int(element_json["width"])
        self.confidence = element_json["confidence"]

    """
	Gets the screen text of the word on the device screen.
	
	:returns: String - the text of the word
	"""
    def get_text(self):
        return self.text

    """
	Gets the starting x location of the word on the device screen.
	
	:returns: int - the starting x location of the word
	"""
    def get_x(self):
        return self.location_x

    """
	Gets the starting y location of the word on the device screen.
	
	:returns: int - the starting y location of the word
	"""
    def get_y(self):
        return self.location_y

    """
	Gets the width (x-axis) of the word on the device screen.
	
	:returns: int - the width of the word
	"""
    def get_width(self):
        return self.width

    """
	Gets the height (y-axis) of the word on the device screen.
	
	:returns: int - the height of the word
	"""
    def get_height(self):
        return self.height

    """
	Gets the screen text confidence as found on the device screen. Only relevant for tesseract based OCR evaluations
    and not GoogleVision.

	:returns: float - the confidence score of the word 
	"""
    def get_confidence(self):
        return self.confidence