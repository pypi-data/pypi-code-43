# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.web import errors

def test_errors(testing_webapp):
	wapp = testing_webapp('errors')
	with wapp.mock() as ctx:
		ctx.view.assert_any_call('error.html')
		ctx.tpl.data.assert_any_call('err500')
		ctx.tpl.data.assert_any_call('err400')
		ctx.wapp.error.assert_any_call(500)
		ctx.wapp.error.assert_any_call(404)
		_check(ctx, errors.err500, 500)
		_check(ctx, errors.err400, 400)

def _check(ctx, handler, code):
	err = ctx.error
	err.status_line = "%d - testing" % code
	err.exception = None
	d = handler(err)
	# ~ x = d['err']
	# ~ assert isinstance(x, dict)
