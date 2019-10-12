from setuptools import setup
def readme():
	with open('README.md') as f:
		README = f.read()
	return README
setup (
	setup_requires=["wheel"],
	name = 'Nesterborn',
	version = '1.6.0',
	py_modules = ['nesternborn'],
	author = 'hfpython',
	author_email = 'hfpython@headfirstlabs.com',
	url = 'http://www.headfirstlabs.com',
	description = 'A simple printer of nested lists',
	long_description = readme(),
	long_description_content_type ='text/markdown',
	packages=['Nester-'],
	Include_package_data=True,
)