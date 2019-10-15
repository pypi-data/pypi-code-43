# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

try:
	from _sadm._version import version as _version
except ImportError:
	_version = 'master'

try:
	from _sadm._version_build import version_build as _version_build
except ImportError:
	_version_build = 'devel'

from _sadm import version

def test_get():
	assert version.get() == _version

def test_build():
	assert version.build() == _version_build

def test_string():
	s = "version %s (build %s)" % (_version, _version_build)
	assert version.string() == '%(prog)s ' + s
