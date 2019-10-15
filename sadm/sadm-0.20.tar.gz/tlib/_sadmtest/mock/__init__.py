# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from contextlib import contextmanager
from os import getenv

from _sadmtest.mock.utils.cmd import MockCmdProc
from _sadmtest.mock.utils.path import MockPath
from _sadmtest.mock.utils.sh import MockShUtil
from _sadmtest.mock.utils.net import MockNet

import _sadm.log
import _sadm.utils.cmd
import _sadm.utils.path
import _sadm.utils.sh
import _sadm.utils.net
import _sadm.utils.vcs.git

__all__ = ['utils', 'log']

def _mockUtils(cfg):
	_sadm.utils.cmd.proc = MockCmdProc(cfg)
	_sadm.utils.path._path = MockPath(cfg)
	_sadm.utils.sh.shutil = MockShUtil(cfg)
	_sadm.utils.net._net = MockNet(cfg)

def _mockUtilsCheck():
	_sadm.utils.path._path.check()
	_sadm.utils.sh.shutil.check()
	_sadm.utils.cmd.proc.check()
	_sadm.utils.net._net.check()

def _mockUtilsRestore():
	_sadm.utils.cmd.proc = _sadm.utils.cmd._ProcMan()
	_sadm.utils.path._path = _sadm.utils.path._Path()
	_sadm.utils.sh.shutil = _sadm.utils.sh._ShUtil()
	_sadm.utils.net._net = _sadm.utils.net._Net()
	_sadm.utils.vcs.git._configDone = False

@contextmanager
def utils(cfg, tag = 'utils'):
	mockcfg = None
	sect = "_sadmtest.mock.%s" % tag
	if cfg and cfg.has_section(sect):
		mockcfg = cfg[sect]
	try:
		print('mock.utils', sect, "cfg=%s" % str(mockcfg is not None))
		_mockUtils(mockcfg)
		yield
		if mockcfg:
			print('mock.utils.check')
			_mockUtilsCheck()
	finally:
		print('mock.utils.restore')
		_mockUtilsRestore()

@contextmanager
def log(level = 'quiet'):
	level = getenv('SADMTEST_LOG', level)
	try:
		print('mock.log', "level=%s" % level)
		if level == 'quiet':
			print('mock.log', 'set env var SADMTEST_LOG=debug to enable debug log')
		_sadm.log._logger = _sadm.log._sysLogger(level)
		_sadm.log._curlevel = level
		yield
	finally:
		print('mock.log.restore')
		del _sadm.log._logger
		_sadm.log._logger = _sadm.log._dummyLogger()
		_sadm.log._curlevel = 'quiet'
