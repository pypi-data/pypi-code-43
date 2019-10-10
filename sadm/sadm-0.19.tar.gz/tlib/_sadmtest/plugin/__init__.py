# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

from hashlib import sha256 as digest
from io import StringIO
from os import path

from _sadm.configure import getPlugin

from _sadmtest import mock
from _sadmtest.check import CheckEnv

__all__ = ['Plugin']

_srcdir = path.dirname(path.dirname(path.dirname(path.dirname(__file__))))

class Plugin(object):
	_p = None
	_env = None
	_envAction = None
	check = None

	def __init__(self, name, env, ns = '_sadm'):
		self._p = getPlugin(name, 'deploy')
		assert self._p.name == name, \
			"plugin %s name error: %s" % (name, self._p.name)
		assert self._p.fullname == "%s.plugin.%s" % (ns, name), \
			"plugin %s fullname error: %s" % (name, self._p.fullname)
		cfgfn = path.join(ns, 'plugin', name.replace('.', path.sep), 'config.ini')
		assert self._p.config.endswith(cfgfn), \
			"plugin %s config error: got: %s - expect: %s" % (name, self._p.config, cfgfn)
		assert self._p.meta.endswith(path.join(ns,
			'plugin', name.replace('.', path.sep), 'meta.json')), \
			"plugin %s meta file error: %s" % (name, self._p.meta)
		self._env = env
		assert self._envSettings() == '', \
			"env %s settings are not empty: %s" % (env.name(), self._envSettings())
		self.check = CheckEnv(self._env)
		from _sadm.env import action as envAction
		self._envAction = envAction

	def _error(self, *args):
		print('ERROR:', *args, file = sys.stderr)
		return False

	def _envSettings(self):
		buf = StringIO()
		self._env.settings.write(buf)
		buf.seek(0, 0)
		return buf.read()

	def _cksum(self, data):
		h = digest(data.encode('utf-8'))
		return h.hexdigest()

	def configure(self):
		self._env.configure()
		fn = path.join(_srcdir, 'tdata', 'plugin',
			self._p.name.replace('.', path.sep), 'default.ini')
		if path.isfile(fn):
			with open(fn, 'r') as fh:
				expect = self._cksum(fh.read())
			got = self._cksum(self._envSettings())
			if got != expect:
				self._error('--')
				self._error(fn)
				self._error('--')
				self._error('expect:', expect)
				with open(fn, 'r') as fh:
					self._error(fh.read())
				self._error('--')
				self._error('   got:', got)
				self._error(self._envSettings())
				self._error('--')
				return False
		else:
			return self._error(fn, 'file not found')
		return True

	def build(self):
		self._envAction.run(self._env, 'build')
		self.check.builddir.content()
		self.check.builddir.envChecksum()

	def deploy(self, mockCfg = 'build.ini'):
		from _sadm.env.settings import Settings
		cfgfn = path.join('tdata', 'plugin',
			self._p.name.replace('.', path.sep), 'config', mockCfg)
		cfg = Settings()
		with open(cfgfn, 'r') as fh:
			cfg.read_file(fh)
		with mock.utils(cfg, 'deploy'):
			self._envAction.run(self._env, 'deploy', sumode = self._p.sumode)
