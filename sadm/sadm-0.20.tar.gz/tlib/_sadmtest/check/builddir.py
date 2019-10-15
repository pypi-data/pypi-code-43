# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from hashlib import sha256, md5
from os import path

class CheckBuilddir(object):
	_env = None
	_rootdir = None
	_deployfn = None
	_envfn = None
	_metadir = None
	_zipfn = None

	def __init__(self, env):
		self._env = "%s/%s" % (env.profile.name(), env.name())
		self._rootdir = env.build.rootdir()
		self._deployfn = self._rootdir + '.deploy'
		self._envfn = self._rootdir + '.env'
		self._metadir = self._rootdir + '.meta'
		self._zipfn = self._rootdir + '.zip'

	def content(self):
		assert path.isdir(self._rootdir), "%s builddir not found" % self._rootdir
		assert path.isfile(self._deployfn), \
			"%s deploy self-extract file not found" % self._deployfn
		assert path.isfile(self._envfn), \
			"%s deploy .env file not found" % self._envfn
		assert path.isdir(self._metadir), \
			"%s build meta dir not found" % self._metadir
		assert path.isfile(self._zipfn), \
			"%s deploy zip file not found" % self._zipfn

	def envChecksum(self):
		with open(self._envfn, 'r') as fh:
			expect = fh.read().strip().split()[0]
		with open(self._zipfn, 'rb') as fh:
			h = sha256(fh.read())
			got = h.hexdigest()
		assert got == expect, \
			"%s env checksum got: %s - expect: %s" % (self._env, got, expect)

	def file(self, name, content = None, checksum = None):
		fn = path.join(self._rootdir, name)
		assert path.isfile(fn), "%s file not found" % fn
		if content is not None:
			with open(fn, 'r') as fh:
				got = fh.read()
			assert got == content, \
				"%s content got: %s - expect: %s" % (fn, got, content)
		if checksum is not None:
			with open(fn, 'rb') as fh:
				h = md5(fh.read())
				got = h.hexdigest()
			assert got == checksum, \
				"%s checksum got: %s - expect: %s" % (fn, got, checksum)
