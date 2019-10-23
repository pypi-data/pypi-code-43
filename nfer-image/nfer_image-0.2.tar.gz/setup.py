from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='nfer_image',
	version='0.2',
	description='utilities for working with images',
        long_description=long_description,
        long_description_content_type='text/x-rst',
	author='Martin Kang',
	author_email='martin@nference.net',
	packages=['nfer_image'],
        package_dir={'':'.'},  # tell disutils packages are under hpa_utils
	install_requires=['matplotlib',
	'numpy',
	'opencv-python',
	'boto3',
	'tqdm',
	'pathlib',
	'scikit-image',
	'sklearn',
	'pandas',
	'tensorflow'],
	zip_safe=False)

