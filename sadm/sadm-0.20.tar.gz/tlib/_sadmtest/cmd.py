# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from contextlib import contextmanager

from _sadm import cfg
from _sadm.cmd import flags

from _sadmtest import mock

class TestingCmd(object):

	def __init__(self, cfgfile):
		self.cfgfile = cfgfile

	@contextmanager
	def mock(self, tag = 'cmd'):
		mockcfg = cfg.new(self.cfgfile)
		program = flags.program
		with mock.log(), mock.utils(mockcfg, tag = tag) as ctx:
			try:
				flags.program = 'sadm'
				yield ctx
			finally:
				flags.program = program
