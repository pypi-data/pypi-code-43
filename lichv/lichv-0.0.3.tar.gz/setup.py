from distutils.core import setup
from setuptools import find_packages

setup(
	name = 'lichv',
	version = '0.0.3',
	description = 'Utility tools with mongodb,mysqldb,sms,semail,brower',
	long_description = 'Utility tools with mongodb,mysqldb,sms,semail,brower', 
	author = 'lichv',
	author_email = 'lichvy@126.com',
	url = 'https://github.com/lichv/python',
	license = '',
	install_requires = [
		'certifi>=2019.9.11',
		'chardet>=3.0.4',
		'configparser>=4.0.2',
		'APScheduler>=3.6.0',
		'idna>=2.8',
		'pycryptodome>=3.9.0',
		'pymongo>=3.9.0',
		'pymysql>=0.9.3',
		'pyyaml>=5.1.2',
		'redis>=3.3.11',
		'bcrypt>=3.1.6',
		'beautifulsoup4>=4.7.1',
		'requests>=2.22.0',
		'tornado>=6.0.3',
		'urllib3>=1.25.6',
		'selenium>=4.0.0a3'
	],
	python_requires='>=3.6',
	keywords = '',
	packages = find_packages('src'),
	package_dir = {'':'src'},
	include_package_data = True,
)
