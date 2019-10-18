from setuptools import setup, find_packages

setup(
	name = "TurnonModbusTCP",
	version = "0.0.3",
	description = "Turnon-Tech for Franka Modbus",
	long_description = "Turnon-Tech for Franka Modbus",
	license = "MIT",

	author = "Kevin Wang",
	author_email = "n159951357753159@gmail.com",
	url="http://pypi.org/user/n159951357753/",

	packages = find_packages(),
	platforms = "any",
	install_requires = ["pyModbusTCP"]
)