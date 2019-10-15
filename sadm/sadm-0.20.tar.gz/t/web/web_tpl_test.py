# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from pytest import raises

def test_data(testing_webapp):
	wapp = testing_webapp('tpl')
	with wapp.mock() as ctx:
		@ctx.orig.tpl.data('testing')
		def tdata():
			return {'tdata': 'testing'}
		d = tdata()
		assert isinstance(d, dict)

def test_error(testing_webapp):
	wapp = testing_webapp('tpl')
	with wapp.mock() as ctx:
		ctx.orig.tpl.data('testing.error')
		with raises(RuntimeError, match = 'testing.error view already registered'):
			ctx.orig.tpl.data('testing.error')
