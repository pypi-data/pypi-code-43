# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from os import path
from unittest.mock import Mock, call

from _sadm import libdir
from _sadm.errors import CommandError

_srcdir = path.dirname(libdir.root())

class MockCmdProc(object):
	_mock = None
	_cfg = None
	_expect = None
	call = None
	check_call = None

	def __init__(self, cfg):
		self._mock = Mock()
		self.call = self._mock.mock_call
		self.check_call = self._mock.mock_check_call
		self.callOutput = self._mock.mock_callOutput
		self._configure(cfg)

	def _configure(self, cfg):
		self._cfg = self._parseConfig(cfg)
		self.call.side_effect = self._sideEffect('call')
		self.check_call.side_effect = self._sideEffect('check_call')
		self.callOutput.side_effect = self._sideEffect('callOutput')

	def _parseConfig(self, cfg):
		d = {}
		if cfg is None:
			return d
		self._expect = {
			'call': deque(),
			'check_call': deque(),
			'callOutput': deque(),
		}
		d['call'] = self._parseCmdOptions(cfg, 'call')
		d['check_call'] = self._parseCmdOptions(cfg, 'check_call')
		d['callOutput'] = self._parseCmdOptions(cfg, 'callOutput')
		return d

	def _parseCmdOptions(self, cfg, opt):
		d = {}
		data = cfg.get('utils.cmd.' + opt, fallback = None)
		if data is None:
			data = cfg.get('cmd.' + opt, fallback = '')
		if data != '':
			for line in data.splitlines():
				line = line.strip()
				if line == '':
					continue
				elif line.startswith('#'):
					continue
				i = line.split(';')
				retval = int(i[0])
				cmdline = ';'.join(i[1:]).strip()
				if cmdline.startswith(path.join('_sadm', 'scripts')):
					cmdline = "%s%s%s" % (_srcdir, path.sep, cmdline)
				d[cmdline] = retval
				self._expect[opt].append(cmdline)
		return d

	def _sideEffect(self, method):
		def wrapper(args, **kwargs):
			if not method in self._cfg:
				raise KeyError("%s method is not configured (yet)" % method)
			if isinstance(args, list):
				cmdline = ' '.join(args)
			else:
				cmdline = args
			try:
				rc = int(self._cfg[method][cmdline])
				if method == 'check_call' and rc != 0:
					raise CommandError("mock error code %d" % rc)
				return rc
			except KeyError as err:
				raise KeyError("%s - %s method" % (str(err), method))
		return wrapper

	def check(self):
		if self._expect is None:
			return
		# call
		got = []
		for x in [x[1][0] for x in self.call.mock_calls]:
			if isinstance(x, list):
				x = ' '.join(x)
			got.append(x)
		expect = list(self._expect['call'])
		assert got == expect, \
			"mock cmd call\ngot:\n%s\nexpect:\n%s" % ('\n'.join(got), '\n'.join(expect))
		# check_call
		got = []
		for x in [x[1][0] for x in self.check_call.mock_calls]:
			if isinstance(x, list):
				x = ' '.join(x)
			got.append(x)
		expect = list(self._expect['check_call'])
		assert got == expect, \
			"mock cmd check_call\ngot:\n%s\nexpect:\n%s" % ('\n'.join(got), '\n'.join(expect))
		# callOutput
		got = []
		for x in [x[1][0] for x in self.callOutput.mock_calls]:
			if isinstance(x, list):
				x = ' '.join(x)
			got.append(x)
		expect = list(self._expect['callOutput'])
		assert got == expect, \
			"mock cmd callOutput\ngot:\n%s\nexpect:\n%s" % ('\n'.join(got), '\n'.join(expect))
