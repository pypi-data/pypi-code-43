# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from unittest.mock import Mock

class MockTmpFile(object):
	_fn = None

	def __init__(self, suffix = None, prefix = None, dir = None, remove = False):
		if suffix is None:
			suffix = '.mock'
		if prefix is None:
			prefix = __name__
		if dir is None:
			dir = '/tmp'
		self._fn = '/'.join([dir, prefix + suffix])

	def __enter__(self):
		return self

	def __exit__(self, *args):
		pass

	def close(self):
		pass

	def unlink(self):
		pass

	def write(self, data):
		pass

	def name(self):
		return self._fn

class MockShUtil(object):
	_expect = None
	_return = None
	_default = None

	def __init__(self, cfg):
		self._expect = []
		self._return = {}
		self._default = {}
		self._mock = Mock()
		self.mktmp = self._mock.mock_mktmp
		self.mktmpdir = self._mock.mock_mktmpdir
		self.getcwd = self._mock.mock_getcwd
		self.makedirs = self._mock.mock_makedirs
		self.chmod = self._mock.mock_chmod
		self.chown = self._mock.mock_chown
		self.chdir = self._mock.mock_chdir
		self.getuid = self._mock.mock_getuid
		self.getgid = self._mock.mock_getgid
		self.lockd = self._mock.mock_lockd
		self.rmtree = self._mock.mock_rmtree
		self.unpack_archive = self._mock.mock_unpack_archive
		self._configure(cfg)

	def _configure(self, cfg):
		self.mktmp.side_effect = self._mktmp
		if cfg is None:
			return
		self._utilsDefault()
		self._parseConfig(cfg)
		self.mktmpdir.side_effect = self._mktmpdir
		self.getcwd.side_effect = self._sideEffect('getcwd')
		self.makedirs.side_effect = self._sideEffect('makedirs')
		self.getuid.side_effect = self._sideEffect('getuid')
		self.getgid.side_effect = self._sideEffect('getgid')
		self.rmtree.side_effect = self._sideEffect('rmtree')
		self.rmtree.side_effect = self._sideEffect('unpack_archive')

	def _utilsDefault(self):
		self._default['getcwd'] = '/testing/workdir'
		self._default['getuid'] = 3000
		self._default['getgid'] = 3000

	def _parseConfig(self, cfg):
		data = cfg.get('utils.sh', fallback = None)
		if data is None:
			data = cfg.get('shutil', fallback = '')
		if data != '':
			for l in data.splitlines():
				l = l.strip()
				if l != '':
					x = l.split(';')
					rtrn = x[0].strip()
					cmdline = ';'.join(x[1:]).strip()
					self._expect.append(cmdline)
					util = cmdline.split(' ')[0].strip()
					self._utilReturn(util, rtrn)

	def _utilReturn(self, name, data):
		if name == '':
			raise RuntimeError('mock shutil: util name is empty')
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
			if util in ('getuid', 'getgid'):
				return int(data)
			return data
		return wrapper

	def _mktmp(self, suffix = None, prefix = None, dir = None, remove = False):
		return MockTmpFile(suffix = suffix, prefix = prefix, dir = dir, remove = remove)

	def _mktmpdir(self, suffix = None, prefix = None):
		if suffix is None:
			suffix = '.mock'
		if prefix is None:
			prefix = __name__
		return prefix + suffix

	def check(self):
		got = []
		for x in self._mock.mock_calls:
			xname = x[0].replace('mock_', '', 1)
			xargs = x[1]
			cmdline = xname
			if len(xargs) > 0:
				cmdline = "%s %s" % (xname, ' '.join([str(i) for i in xargs]))
			xkwargs = x[2]
			for k, v in xkwargs.items():
				v = str(v)
				cmdline = "%s, %s=%s" % (cmdline, k, v)
			got.append(cmdline)
		assert got == self._expect, \
			"mock shutil\n*** GOT:\n%s\n*** EXPECT:\n%s" % ('\n'.join(got), '\n'.join(self._expect))
