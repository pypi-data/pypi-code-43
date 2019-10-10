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

__all__ = ['get', 'build', 'string']

def get():
	return _version

def build():
	return _version_build

def string(prog = None):
	s = "%s (build %s)" % (get(), build())
	if prog is None:
		return '%(prog)s version ' + s
	return "%s version %s" % (prog, s)
