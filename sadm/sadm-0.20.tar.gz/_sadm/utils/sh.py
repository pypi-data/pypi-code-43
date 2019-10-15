# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import os
import os.path
import shutil as _sh

from contextlib import contextmanager

from .tmpdir import TmpDir
from .tmpfile import TmpFile

__all__ = ['makedirs', 'chmod', 'chown', 'mktmp', 'mktmpdir', 'getcwd', 'chdir',
	'getuid', 'getgid', 'lockd', 'rmtree']

class _ShUtil(object):
	def __init__(self):
		self.makedirs = os.makedirs
		self.chmod = os.chmod
		self.chown = _sh.chown
		self.mktmp = self._mktmp
		self.mktmpdir = self._mktmpdir
		self.getcwd = os.getcwd
		self.chdir = os.chdir
		self.getuid = os.getuid
		self.getgid = os.getgid
		self.lockd = self._lockd
		self.rmtree = _sh.rmtree
		self.unpack_archive = _sh.unpack_archive

	def _mktmp(self, suffix = None, prefix = None, dir = None, remove = False):
		return TmpFile(suffix = suffix, prefix = prefix, dir = dir, remove = remove)

	def _mktmpdir(self, suffix = None, prefix = None, dir = None, rmtree = False):
		return TmpDir(suffix = suffix, prefix = prefix, dir = dir, rmtree = rmtree)

	def _lockd(self, path):
		fn = os.path.join(path, '.sadmlock')
		try:
			with open(fn, 'x') as fh:
				fh.write('1\n')
				fh.flush()
			yield
		finally:
			os.unlink(fn)

shutil = _ShUtil()

def makedirs(name, mode = 0o0755, exists_ok = False):
	return shutil.makedirs(name, mode = mode, exist_ok = exists_ok)

def chmod(path, mode):
	return shutil.chmod(path, mode)

def chown(path, user = None, group = None):
	return shutil.chown(path, user = user, group = group)

def mktmp(suffix = None, prefix = None, dir = None, remove = False):
	return shutil.mktmp(suffix = suffix, prefix = prefix, dir = dir, remove = remove)

def mktmpdir(suffix = None, prefix = None, dir = None, rmtree = False):
	return shutil.mktmpdir(suffix = suffix, prefix = prefix, dir = dir, rmtree = rmtree)

def getcwd():
	return shutil.getcwd()

def chdir(path):
	return shutil.chdir(path)

def getuid():
	return shutil.getuid()

def getgid():
	return shutil.getgid()

@contextmanager
def lockd(path):
	try:
		yield shutil.lockd(path)
	finally:
		pass

def rmtree(path):
	return shutil.rmtree(path)

def unpack_archive(filename, extract_dir = None, format = None):
	shutil.unpack_archive(filename, extract_dir = extract_dir, format = format)
