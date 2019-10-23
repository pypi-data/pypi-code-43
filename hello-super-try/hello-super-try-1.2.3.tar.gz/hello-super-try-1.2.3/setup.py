
from setuptools import find_packages, setup

INSTALL_REQUIREMENTS = [
    'requests>=2.21.0'
]

setup(
	name="hello-super-try",
	version="1.2.3",
	packages=find_packages(),
	include_package_data=True,
	package_dir={'': '.'},
	descriptions="DESCRIPTION FTW!"
)
