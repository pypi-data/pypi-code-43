"""Source of exception classes for Scrapedia's pipelines.

Classes: ScrapediaError, ScrapediaRequestError, ScrapediaSearchError,
ScrapediaParseError
"""

class ScrapediaError(Exception):
	"""Generic error to be implemented by further classes in order to uncouple
	Scrapedia's exceptions from others.
	"""
	pass


class ScrapediaRequestError(Exception):
	"""Error to be raised whenever a requester fails when trying to fetch a
	web page.
	"""
	pass


class ScrapediaSearchError(Exception):
	"""Error to be raised whenever a seeker fails to find the expected excerpt
	of text on the web page's content.
	"""
	pass


class ScrapediaParseError(Exception):
	"""Error to be raised whenever a parser fails to parse the text or when
	the expected data is not found.
	"""
	pass
