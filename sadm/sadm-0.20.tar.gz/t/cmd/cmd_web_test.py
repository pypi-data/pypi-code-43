# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from unittest.mock import Mock

import _sadm.web.app

from _sadm.cmd import web

def test_main(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('web_main'):
		wapp = _sadm.web.app.wapp
		syslog = web.syslog
		try:
			mock_wapp = Mock()
			_sadm.web.app.wapp = mock_wapp
			web.syslog = Mock()
			web.main(argv = [])
			mock_wapp.run.assert_called_with(debug = False, host = 'localhost',
				port = 3478, quiet = True, reloader = False)
			web.syslog.init.assert_called_once()
			web.syslog.close.assert_called_once()
		finally:
			del _sadm.web.app.wapp
			_sadm.web.app.wapp = wapp
			del web.syslog
			web.syslog = syslog

def test_debug(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('web_debug'):
		wapp = _sadm.web.app.wapp
		syslog = web.syslog
		try:
			mock_wapp = Mock()
			_sadm.web.app.wapp = mock_wapp
			web.syslog = Mock()
			web.main(argv = ['--debug'])
			mock_wapp.run.assert_called_with(debug = True, host = 'localhost',
				port = 3478, quiet = False, reloader = True)
		finally:
			del _sadm.web.app.wapp
			_sadm.web.app.wapp = wapp
			del web.syslog
			web.syslog = syslog

def test_run(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('web_start'):
		wapp = _sadm.web.app.wapp
		try:
			mock_wapp = Mock()
			_sadm.web.app.wapp = mock_wapp
			_sadm.web.app.run('testing.host', 1234, False)
			mock_wapp.run.assert_called_with(debug = False, host = 'testing.host',
				port = 1234, quiet = True, reloader = False)
		finally:
			del _sadm.web.app.wapp
			_sadm.web.app.wapp = wapp
