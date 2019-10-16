
class By:

    """
	Constructs a text based locator to search for within the text on the device screen.
	
	:param text: - String The text to search for on the device screen, i.e. "hello world"
	:returns: The constructed locator
	"""
    def text(self, text):
        return "By.Text: " + text
    
    """
	Constructs an image based locator to search for within the the device screen. The input
	can be either an absolute file path to a .png file on your machine, OR can be a url
	to a .png
	
	:param path_or_url_to_image_snippet_png: - The path or URL to an image snippet to search for within the device screen.
	:returns: The constructed locator
	"""
    def image(self, path_or_url_to_image_snippet_png):
        return "By.Image: " + path_or_url_to_image_snippet_png