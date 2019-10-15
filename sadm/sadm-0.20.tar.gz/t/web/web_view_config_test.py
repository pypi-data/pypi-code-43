# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.web.view import config

def test_config(testing_webapp):
	wapp = testing_webapp('view')
	with wapp.mock() as ctx:
		d = config.index()
		ctx.wapp.route.assert_any_call('/config')
		ctx.view.assert_any_call('config.html')
		ctx.tpl.data.assert_any_call('config')
		assert sorted(d.keys()) == ['cfg', 'cfgfile']
