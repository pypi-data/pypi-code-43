from setuptools import setup

setup(
	name = 'pgsql',
	py_modules = ['pgsql'],
	version = '1.2',
	description = 'PostgreSQL client library for Python 3',
	long_description = open('README').read(),
	author = 'Antti Heinonen',
	author_email = 'antti@heinonen.cc',
	url = 'https://antti.heinonen.cc',
	license = 'MIT',
	platforms = ['POSIX'],
	python_requires = '>=3',
	classifiers = [
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3',
		'Topic :: Database',
		'Topic :: Software Development :: Libraries :: Python Modules'
	]
)
