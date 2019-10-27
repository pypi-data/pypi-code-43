
from setuptools import find_packages, setup

INSTALL_REQUIREMENTS = [
    'requests>=2.21.0'
]

setup(
	name="super-hiper-hello",
	version="0.0.1",
	packages=find_packages(),
	include_package_data=True,
	package_dir={'': '.'},
	install_requires=INSTALL_REQUIREMENTS,
	description="HELLO DESCRIPTION FTW!"
)
