# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import os
import shutil
import tempfile

__all__ = ['TmpDir']

class TmpDir(object):
	_dn = None
	_rm = None

	def __init__(self, suffix = None, prefix = None, dir = None, rmtree = False):
		if prefix and not prefix.endswith('.'):
			prefix = "%s." % prefix
		self._dn = tempfile.mkdtemp(suffix = suffix, prefix = prefix, dir = dir)
		self._rm = rmtree

	def __enter__(self):
		return self._dn

	def __exit__(self, *args):
		if self._rm:
			self.rmtree()

	def __str__(self):
		return self._dn

	def rmtree(self):
		shutil.rmtree(self._dn)
