from ephysiopy import __version__
import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setuptools.setup(name='ephysiopy',
	  version=__version__,
	  description='Analysis of electrophysiological data recorded with the Axona or OpenEphys recording systems',
	  long_description=long_description,
	  long_description_content_type='text/markdown',
	  url='https://github.com/rhayman/ephysiopy',
	  author='Robin Hayman',
	  author_email='r.hayman@ucl.ac.uk',
	  license='MIT',
	  packages=setuptools.find_packages(),
	  package_data={'ephysiopy' : ['dacq2py/*.pkl']},
	  python_requires='>=3.5',
	  install_requires=[
	  	'numpy',
	  	'scipy',
	  	'matplotlib',
	  	'astropy',
	  	'scikit-image',
	  	'mahotas',
	  	'sklearn'
	  ],
	  zip_safe=False)
