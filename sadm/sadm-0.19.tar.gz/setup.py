#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

# https://packaging.python.org/guides/distributing-packages-using-setuptools/

from datetime import datetime
from os import makedirs, path, unlink
from setuptools import setup, find_packages
from sys import argv

def _clean():
	for n in ('_version.py', '_version_build.py'):
		fn = path.join('_sadm', n)
		if path.isfile(fn):
			unlink(fn)

def _buildInfo():
	now = datetime.utcnow()
	with open('./_sadm/_version_build.py', 'w') as fh:
		fh.write('# auto-generated file\n')
		fh.write("version_build = '%s'\n" % now.strftime('%y%m%d.%H%M%S'))

def main():

	try:
		cmd = argv[1]
	except IndexError:
		cmd = 'none'

	with open('requirements.txt', 'r') as fh:
		deps = fh.read().splitlines()

	_buildInfo()

	setup(
		author = 'Jeremías Casteglione',
		author_email = 'jrmsdev@gmail.com',
		python_requires = '~=3.6',
		setup_requires = ['wheel>=0.33', 'setuptools_scm>=3.3'],
		install_requires = deps,
		use_scm_version = {
			'write_to': '_sadm/_version.py',
			'fallback_version': '0.0',
		},
		py_modules = ['sadm'],
		packages = find_packages(),
		include_package_data = True,
	)

	if cmd == 'clean':
		_clean()

if __name__ == '__main__':
	main()
