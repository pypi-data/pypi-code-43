# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from http.client import HTTPResponse
from unittest.mock import Mock

class MockNet(object):
	_expect = None
	_return = None
	_default = None

	def __init__(self, cfg):
		self._expect = []
		self._return = {}
		self._default = {}
		self._mock = Mock()
		self.urlopen = self._mock.urlopen
		self._configure(cfg)

	def _configure(self, cfg):
		# ~ self._setDefaults()
		self.urlopen.side_effect = self._urlopen
		if cfg is None:
			return
		self._parseConfig(cfg)

	def _parseConfig(self, cfg):
		data = cfg.get('utils.net', fallback = None)
		if data is None:
			data = cfg.get('net', fallback = '')
		if data != '':
			for l in data.splitlines():
				l = l.strip()
				if l != '':
					x = l.split(';')
					rtrn = x[0].strip()
					cmdline = ';'.join(x[1:]).strip()
					util = cmdline.split(' ')[0].strip()
					self._expect.append(cmdline)
					self._utilReturn(util, rtrn)

	# ~ def _setDefaults(self):
		# ~ self._default['urlopen'] = None

	def _utilReturn(self, name, data):
		if name == '':
			raise RuntimeError('mock utils.net: util name is empty')
		if self._return.get(name, None) is None:
			self._return[name] = deque()
		self._return[name].appendleft(data)

	def _sideEffect(self, util):
		def wrapper(*args, **kwargs):
			rtrn = self._return.get(util, None)
			if rtrn is None:
				return self._default.get(util, None)
			try:
				data = rtrn.pop()
			except IndexError:
				return self._default.get(util, None)
			if data == '':
				return self._default.get(util, None)
			return data
		return wrapper

	def check(self):
		got = []
		for x in self._mock.mock_calls:
			xname = x[0]
			xargs = x[1]
			cmdline = xname
			if len(xargs) > 0:
				if xname == 'urlopen':
					cmdline = "%s %s" % (xname, str(xargs[0]))
					xkwargs = x[2]
					for k, v in xkwargs.items():
						v = str(v)
						if k == 'data':
							if v:
								v = True
							else:
								v = False
						cmdline = "%s, %s=%s" % (cmdline, k, v)
				else:
					cmdline = "%s %s" % (xname, ' '.join([str(i) for i in xargs]))
					xkwargs = x[2]
					for k, v in xkwargs.items():
						v = str(v)
						cmdline = "%s, %s=%s" % (cmdline, k, v)
			got.append(cmdline)
		assert got == self._expect, \
			"mock utils.net\ngot:\n%s\nexpect:\n%s" % ('\n'.join(got), '\n'.join(self._expect))

	def _urlopen(self, url, data = None, timeout = None, context = None):
		resp = HTTPResponse(Mock())
		data = self._return.get('urlopen', None)
		resp.status = int(data.pop().strip())
		resp.reason = 'Mock not configured'
		return resp
