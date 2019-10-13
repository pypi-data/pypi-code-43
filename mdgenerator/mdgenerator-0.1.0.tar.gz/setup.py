from setuptools import setup

with open('README.md') as f:
	long_description = f.read()

with open('requirements.txt') as f:
	requirements = f.readlines()

setup(
	name='mdgenerator',
	version='0.1.0',
	author='Nilan Saha',
	description = 'Package to generate different kind of markdown texts',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	url = 'https://github.com/nilansaha/mdgenerator',
	license = 'Apache 2.0',
	packages = ['mdgenerator'],
	install_requires = requirements,
	python_requires='>=3.6',
	classifiers = [
		'Programming Language :: Python'
	],
	entry_points = {
		'console_scripts': [
			'mdgenerator = mdgenerator.cli:main'
		]
	}
)
