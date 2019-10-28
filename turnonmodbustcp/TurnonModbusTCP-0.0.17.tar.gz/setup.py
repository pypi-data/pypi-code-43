from setuptools import setup, find_packages

with open("README.md", "r") as fh:
	long_txt = fh.read()

setup(
	name = "TurnonModbusTCP",
	version = "0.0.17",
	description = "Turnon-Tech for Franka Modbus",
	long_description = long_txt,
	long_description_content_type = "text/markdown",
	license = "MIT",

	author = "Kevin Wang",
	author_email = "n159951357753159@gmail.com",
	url="http://pypi.org/user/n159951357753/",

	packages = find_packages(),
	install_requires = ["pyModbusTCP"],
	python_requires= ">=3.6"
	
)