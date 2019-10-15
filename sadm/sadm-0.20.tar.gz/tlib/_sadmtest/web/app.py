# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle

from contextlib import contextmanager
from os import path
from unittest.mock import Mock

from _sadm import cfg

from _sadmtest import mock
from _sadmtest.wapp import TestingWebapp

__all__ = ['WebApp']

def _mock_decorator(*args, **kwargs):
	def wrapper(func):
		def decorator(*args, **kwargs):
			return func(*args, **kwargs)
		return decorator
	return wrapper

_mock = Mock()
_orig = Mock()

import _sadm.web.app

_orig.view = _sadm.web.app.view
_sadm.web.app.view = _mock.view
_sadm.web.app.view.side_effect = _mock_decorator

_orig.wapp = _sadm.web.app.wapp
_sadm.web.app.wapp = _mock.wapp
_sadm.web.app.wapp.route.side_effect = _mock_decorator
_sadm.web.app.wapp.error.side_effect = _mock_decorator

import _sadm.web.tpl

_orig.tpl = _sadm.web.tpl
_sadm.web.tpl = _mock.tpl
_sadm.web.tpl.data.side_effect = _mock_decorator

class WebApp(TestingWebapp):
	name = 'web'

	@contextmanager
	def mock(self, tag = 'webapp'):
		mockcfg = None
		if path.isfile(self.cfgfn):
			mockcfg = cfg.new(self.cfgfn)
		with mock.log(), mock.utils(mockcfg, tag = tag):
			ctx = Mock()
			ctx.orig = _orig
			ctx.view = _mock.view
			ctx.wapp = _mock.wapp
			ctx.tpl = _mock.tpl
			try:
				yield ctx
			finally:
				pass
