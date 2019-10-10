# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import os
import os.path

__all__ = ['sep', 'isfile', 'isdir', 'join', 'abspath', 'normpath', 'unlink']

class _Path(object):
	def __init__(self):
		self.sep = os.path.sep
		self.isfile = os.path.isfile
		self.isdir = os.path.isdir
		self.join = os.path.join
		self.abspath = os.path.abspath
		self.normpath = os.path.normpath
		self.unlink = os.unlink

_path = _Path()

sep = _path.sep

def isfile(name):
	return _path.isfile(name)

def isdir(name):
	return _path.isdir(name)

def join(base, *parts):
	if base.startswith('~'):
		base = os.path.expanduser(base)
	return _path.join(base, *parts)

def abspath(name):
	return _path.abspath(name)

def normpath(name):
	return _path.normpath(name)

def unlink(name):
	_path.unlink(name)
