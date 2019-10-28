from setuptools import setup

from veracitysdk import __version__


setup(
	name = "veracitysdk",
	version = __version__,
	description = "Veracity api library",
	author = "schen",
	author_email = "shu@disinformationindex.org",
	url = "https://bitbucket.org/disinformationindex/veracitysdk/src",
	py_modules = ["veracitysdk"],
)
