from setuptools import setup

__project__ = "motivate1234"
__version__ = "0.0.9"
__description__ = "this version included text file"
__packages__ = ["motivate1234"]

setup(
	name = __project__,
	version = __version__,
	description = __description__,
	packages = __packages__,
	include_package_data=True,
	zip_safe=False)

