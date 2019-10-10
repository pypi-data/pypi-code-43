# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path, environ
from subprocess import TimeoutExpired

from _sadm import log, libdir
from _sadm.errors import PluginScriptNotFound, PluginScriptNoExec, PluginScriptTimeout
from _sadm.utils import cmd

__all__ = ['Scripts']

_TTL = 180

class Scripts(object):
	_dir = None
	_env = None

	def __init__(self, pname, dist, sdir = None):
		if sdir is None:
			sdir = libdir.fpath('scripts', dist, pname.replace('.', path.sep))
		self._dir = sdir
		log.debug("%s" % self._dir)
		self._env = environ.copy()

	def run(self, script, args = tuple()):
		spath = path.join(self._dir, script)
		log.debug("run %s %s" % (spath, args))
		s = _Script(spath, args)
		return s.dispatch(env = self._env)

class _Script(object):
	_cmd = None

	def __init__(self, script, args):
		self._cmd = [script]
		self._cmd.extend(args)

	def dispatch(self, env = None):
		if env is None:
			env = environ.copy()
		try:
			return cmd.call(self._cmd, env = env, timeout = _TTL)
		except FileNotFoundError:
			raise PluginScriptNotFound(self._cmd[0])
		except PermissionError:
			raise PluginScriptNoExec(self._cmd[0])
		except TimeoutExpired:
			raise PluginScriptTimeout("%s after %s seconds" % (self._cmd[0], _TTL))
