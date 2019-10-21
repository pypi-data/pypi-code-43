import os
from setuptools import setup

setup(
	name = 'ql-cq',
	author = 'Quantlane',
	author_email = 'code@quantlane.com',
	version =  open('version.txt').read().strip(),
	url = 'https://gitlab.com/quantlane/meta/cq',
	license = 'Apache License, Version 2.0',
	long_description = open('README.md').read(),
	long_description_content_type = 'text/markdown',
	install_requires = [
		'pylint==2.3.1',
		'pyflakes-ext==1.0.4',
		'mypy==0.740',
		'click>=3.0,<8.0',
		'toolz>=0.8.2,<1.0.0',
		'requirements-parser>=0.1.0',
		'pip>=19.0.0',
		'bellybutton==0.2.5',
		'astpath[xpath]==0.6.1', # dependency of bellybutton, higher versions crash it
	],
	packages = ['cq', 'cq.checkers'],
	package_data = {'cq': ['checkers/pylintrc', 'checkers/.bellybutton.yml']},
	entry_points = {
		'console_scripts': [
			'cq=cq.main:main'
		]
	}
)
