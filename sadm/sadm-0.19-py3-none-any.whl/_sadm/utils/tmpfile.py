# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import os
import tempfile

__all__ = ['TmpFile']

class TmpFile(object):
	_fd = None
	_fn = None
	_rm = None

	def __init__(self, suffix = None, prefix = None, dir = None, remove = False):
		if prefix and not prefix.endswith('.'):
			prefix = "%s." % prefix
		self._fd, self._fn = tempfile.mkstemp(suffix = suffix,
			prefix = prefix, dir = dir, text = False)
		self._rm = remove

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.close()
		if self._rm:
			self.unlink()

	def close(self):
		os.close(self._fd)

	def unlink(self):
		os.unlink(self._fn)

	def write(self, data):
		if isinstance(data, str):
			data = data.encode('utf-8')
		os.write(self._fd, data)

	def name(self):
		return self._fn
