from setuptools import setup

setup(name='hpa_utils',
	version='0.1',
	description='utilities for downloading and processing image data from nference Human Protein Atlas collection',
	author='Martin Kang',
	author_email='martin@nference.net',
	packages=['hpa_utils'],
	install_requires=['matplotlib',
	'numpy',
	'opencv-python',
	'boto3',
	'tqdm',
	'pathlib',
	'skimage',
	'sklearn'],
	zip_safe=False)
	