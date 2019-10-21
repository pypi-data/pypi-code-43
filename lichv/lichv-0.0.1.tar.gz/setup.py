from distutils.core import setup
from setuptools import find_packages

setup(
	name = 'lichv',
	version = '0.0.1',
	description = 'Utility tools with mongodb,mysqldb,sms,semail,brower',
	long_description = 'Utility tools with mongodb,mysqldb,sms,semail,brower', 
	author = 'lichv',
	author_email = 'lichvy@126.com',
	url = 'https://github.com/lichv/python',
	license = '',
	install_requires = [
		'certifi>=2019.9.11',
		'chardet>=3.0.4',
		'idna>=2.8',
		'pycryptodome>=3.9.0',
		'pymongo>=3.9.0',
		'PyMySQL>=0.9.3',
		'PyYAML>=5.1.2',
		'redis>=3.3.11',
		'requests>=2.22.0',
		'tornado>=6.0.3',
		'urllib3>=1.25.6',
		'selenium>=3.141.0'
	],
	python_requires='>=3.6',
	keywords = '',
	packages = find_packages('src'),
	package_dir = {'':'src'},
	include_package_data = True,
)
