from distutils.core import setup
from setuptools import find_packages

setup(
	name = 'lichv',
	version = '0.0.8',
	description = 'Utility tools with mongodb,mysqldb,sms,semail,brower',
	long_description = 'Utility tools with mongodb,mysqldb,sms,semail,brower', 
	author = 'lichv',
	author_email = 'lichvy@126.com',
	url = 'https://github.com/lichv/python',
	license = '',
	install_requires = [
		'requests>=2.22.0',
		'pyyaml>=5.1.2',
		'pymongo>=3.9.0',
		'pymysql>=0.9.3',
		'selenium>=3.141.0'
	],
	python_requires='>=3.6',
	keywords = '',
	packages = find_packages('src'),
	package_dir = {'':'src'},
	include_package_data = True,
)
