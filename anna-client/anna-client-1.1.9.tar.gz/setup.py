import setuptools

with open('README.md', 'r') as f:
	description = f.read()

setuptools.setup(
	name='anna-client',
	version='1.1.9',
	author='Patrik Pihlstrom',
	author_email='patrik.pihlstrom@gmail.com',
	url='https://github.com/patrikpihlstrom/anna-client',
	description='anna API client',
	long_description=description,
	long_description_content_type='text/markdown',
	packages=['anna_client'],
	install_requires=[
		'requests',
		'graphqlclient'
	]
)
