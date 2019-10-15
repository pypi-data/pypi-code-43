# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from pytest import raises
from unittest.mock import Mock

import _sadm.listen

from _sadm.cmd import listen
from _sadm.errors import CommandError

def test_bottle(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('listen_bottle'):
		wapp = _sadm.listen.wapp
		try:
			mock_bottle = Mock()
			mock_wapp = Mock()
			mock_wapp.init = Mock(return_value = mock_bottle)
			_sadm.listen.wapp = mock_wapp
			listen.bottle()
			_check(mock_wapp, mock_bottle)
		finally:
			del _sadm.listen.wapp
			_sadm.listen.wapp = wapp

def _check(wapp, w):
	wapp.init.assert_called_with()
	wapp.config.getboolean.assert_called_with('sadm.listen', 'debug', fallback = False)
	wapp.config.get.assert_called_with('sadm.listen', 'host', fallback = '127.0.0.1')
	wapp.config.getint.assert_called_with('sadm.listen', 'port', fallback = 3666)
	w.run.assert_called_once()

def test_uwsgi(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('listen_uwsgi'):
		exec_prefix = listen.sys.exec_prefix
		libfpath = listen.libdir.fpath
		try:
			listen.sys.exec_prefix = '/opt/sadm'
			listen.libdir.fpath = _libfpath
			listen.uwsgi()
		finally:
			del listen.sys.exec_prefix
			listen.sys.exec_prefix = exec_prefix
			listen.libdir.fpath = libfpath

def _libfpath(*parts):
	fn = '/'.join(parts)
	return '/opt/src/' + fn

def test_uwsgi_error(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('listen_uwsgi_error'):
		exec_prefix = listen.sys.exec_prefix
		libfpath = listen.libdir.fpath
		try:
			listen.sys.exec_prefix = '/opt/sadm'
			listen.libdir.fpath = _libfpath
			with raises(CommandError, match = 'mock error code 9'):
				listen.uwsgi()
		finally:
			del listen.sys.exec_prefix
			listen.sys.exec_prefix = exec_prefix
			listen.libdir.fpath = libfpath
