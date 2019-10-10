# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle

from os import path

from _sadmtest.listen.webhook import TestingTask
from _sadmtest.listen.webhook.repo.provider import TestingProvider
from _sadmtest.wapp import TestingWebapp

import _sadm.listen.errors

import _sadm.listen.wapp
_sadm.listen.wapp._cfgfn = path.join('tdata', 'listen.cfg')

import _sadm.listen.webhook.repo
_sadm.listen.webhook.repo._provider['testing'] = TestingProvider()

import _sadm.listen.exec
_sadm.listen.exec._pycmd = '/opt/sadm/bin/python3'
_sadm.listen.exec._selfpath = '/opt/src/sadm/listen/exec.py'

import _sadm.listen.handlers.exec
_sadm.listen.handlers.exec._taskman['testing'] = TestingTask()

class ListenWebapp(TestingWebapp):
	name = 'listen'

	def __enter__(self):
		print("listen wapp init %s" % self.profile)
		fn = path.join('tdata', 'listen.cfg')
		if self.profile != '.':
			fn = path.join('tdata', 'listen', self.profile, 'listen.cfg')
		_sadm.listen.wapp.wapp = _sadm.listen.wapp.init(cfgfn = fn)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		print("listen wapp exit %s" % self.profile)
		del _sadm.listen.wapp.config
		_sadm.listen.wapp.config = None
		del _sadm.listen.wapp.wapp
		_sadm.listen.wapp.wapp = bottle.Bottle()
		_sadm.listen.errors._initDone = False

	@property
	def routes(self):
		return _sadm.listen.wapp.wapp.routes

	@property
	def plugins(self):
		return _sadm.listen.wapp.wapp.plugins
