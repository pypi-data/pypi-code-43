# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.web.view import home

def test_index(testing_webapp):
	wapp = testing_webapp('view')
	with wapp.mock() as ctx:
		d = home.index()
		ctx.wapp.route.assert_any_call('/')
		ctx.view.assert_any_call('index.html')
		ctx.tpl.data.assert_any_call('home')
		assert sorted(d.keys()) == ['cfg', 'cfgfile', 'user']
