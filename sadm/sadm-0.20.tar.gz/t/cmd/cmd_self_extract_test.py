# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from contextlib import contextmanager
from unittest.mock import Mock, call, mock_open

from _sadm.deploy import self_extract

_rootdir = '/opt/sadm'

@contextmanager
def mock():
	ctx = Mock()
	path = self_extract.path
	makedirs = self_extract.makedirs
	chmod = self_extract.chmod
	unlink = self_extract.unlink
	call = self_extract.call
	try:
		self_extract._cargo = {}
		self_extract._vars = {
			'env': 'testing',
			'rootdir': _rootdir,
		}
		ctx.path = Mock()
		ctx.path.join.side_effect = lambda *p: '/'.join(p)
		ctx.makedirs = Mock()
		ctx.chmod = Mock()
		ctx.unlink = Mock()
		ctx.call = Mock()
		self_extract.path = ctx.path
		self_extract.makedirs = ctx.makedirs
		self_extract.chmod = ctx.chmod
		self_extract.unlink = ctx.unlink
		self_extract.call = ctx.call
		yield ctx
	finally:
		del self_extract._cargo
		self_extract._cargo = {}
		del self_extract._vars
		self_extract._vars = {}
		del self_extract.path
		self_extract.path = path
		del self_extract.makedirs
		self_extract.makedirs = makedirs
		del self_extract.chmod
		self_extract.chmod = chmod
		del self_extract.unlink
		self_extract.unlink = unlink
		del self_extract.call
		self_extract.call = call

def test_main():
	with mock() as ctx:
		ctx.call.return_value = 0
		rc = self_extract.main()
		assert ctx.path.join.mock_calls == [
			call(_rootdir, 'env'),
			call(_rootdir+'/env', 'testing.env'),
			call(_rootdir, 'bin', 'sadm'),
		]
		ctx.makedirs.assert_called_with('/opt/sadm/env', exist_ok = True)
		ctx.chmod.assert_called_with('/opt/sadm/env', 0o700)
		assert ctx.call.mock_calls == [
			call('/opt/sadm/bin/sadm import /opt/sadm/env/testing.env', shell = True),
			call('/opt/sadm/bin/sadm --env testing deploy', shell = True),
		]
		assert rc == 0

def test_import_error():
	with mock() as ctx:
		ctx.call.return_value = 9
		rc = self_extract.main()
		ctx.call.assert_called_with('/opt/sadm/bin/sadm import /opt/sadm/env/testing.env',
			shell = True)
		assert rc == 9

def test_deploy_error():
	def mock_call(cmd, **kwargs):
		if cmd.endswith('--env testing deploy'):
			return 9
		return 0
	with mock() as ctx:
		ctx.call.side_effect = mock_call
		rc = self_extract.main()
		assert ctx.call.mock_calls == [
			call('/opt/sadm/bin/sadm import /opt/sadm/env/testing.env', shell = True),
			call('/opt/sadm/bin/sadm --env testing deploy', shell = True),
		]
		assert rc == 9

def test_extract():
	with mock() as ctx:
		ctx.call.return_value = 9
		ctx.path.isfile.return_value = True
		self_extract._cargo.update({
			'testing.txt': 'data',
		})
		b64decode = self_extract.b64decode
		try:
			self_extract.open = mock_open()
			self_extract.b64decode = Mock()
			self_extract.b64decode.return_value = 'testing'
			rc = self_extract.main()
		finally:
			self_extract.open.assert_called_with('/'.join((_rootdir, 'env', 'testing.txt')), 'wb')
			self_extract.b64decode.assert_called_once_with(b'data')
			fh = self_extract.open()
			fh.write.assert_called_once_with('testing')
			del self_extract.open
			self_extract.b64decode = b64decode
		ctx.call.assert_called_with('/opt/sadm/bin/sadm import /opt/sadm/env/testing.env',
			shell = True)
		ctx.path.join.assert_any_call('/opt/sadm/env', 'testing.txt')
		ctx.path.isfile.assert_called_once_with('/opt/sadm/env/testing.txt')
		ctx.unlink.assert_called_once_with('/opt/sadm/env/testing.txt')
		assert rc == 9
