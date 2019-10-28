from setuptools import setup

setup(
	name='airbornerf-sdk',
	version='1.0.6',
	description='AirborneRF SDK',
	packages=['airbornerf'],
	license='Proprietary',
	author='Thomas Wana',
	author_email='support@airbornerf.com',
	url='https://www.airbornerf.com/',
	install_requires=[
		'requests'
	],
)
