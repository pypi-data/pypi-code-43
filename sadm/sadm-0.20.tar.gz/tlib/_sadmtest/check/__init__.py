# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from .builddir import CheckBuilddir

class CheckEnv(object):
	_env = None
	builddir = None

	def __init__(self, env):
		self._env = env
		self.builddir = CheckBuilddir(self._env)
