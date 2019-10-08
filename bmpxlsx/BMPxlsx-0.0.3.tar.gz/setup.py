#from distutils.core import setup
from setuptools import setup, Extension

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
	name = 'BMPxlsx',
	packages = ['BMPxlsx'],
	version = '0.0.3',
	license='MIT',
	description = 'The library takes a dictionary of form {Sheet: {Cell: Value}} and updates the specified Excel file accordingly.',
	long_description=long_description,
	long_description_content_type='text/markdown',  
	author = 'Mike Campagna',
	author_email = 'msc94@drexel.edu',
	url = 'https://github.com/TheAcademyofNaturalSciences/BMPxlsx',
	download_url = 'https://github.com/TheAcademyofNaturalSciences/BMPxlsx/archive/v_003.tar.gz',
	keywords = ['Excel', 'Write', 'XLSX', 'BMP'],
	install_requires=['openpyxl'],
	classifiers=[
		'Development Status :: 3 - Alpha', # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7'
	],
)
