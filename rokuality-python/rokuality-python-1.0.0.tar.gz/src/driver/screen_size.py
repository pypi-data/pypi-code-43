
class ScreenSize:

    width = None
    height = None

    def __init__(self, element_json):
        self.width = int(element_json["screen_width"])
        self.height = int(element_json["screen_height"])

    """
	Gets the width of the device screen.
	
    :returns: the screen width
	"""
    def get_width(self):
        return self.width

    """
	Gets the height of the device screen.
	
    :returns: the screen height
	"""
    def get_height(self):
        return self.height