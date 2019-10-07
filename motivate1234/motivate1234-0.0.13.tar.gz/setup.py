from setuptools import setup

__project__ = "motivate1234"
__version__ = "0.0.13"
__description__ = "this version included bash"
__packages__ = ["motivate1234"]

setup(
	name = __project__,
	version = __version__,
	description = __description__,
	packages = __packages__,
	include_package_data = True,
	scripts = ['/home/pi/.local/lib/python3.7/site-packages/motivate1234/run_echo'])

