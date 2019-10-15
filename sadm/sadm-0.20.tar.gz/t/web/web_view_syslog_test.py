# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.web.view import syslog

def test_index(testing_webapp):
	wapp = testing_webapp('view')
	with wapp.mock() as ctx:
		d = syslog.index()
		ctx.wapp.route.assert_any_call('/syslog')
		ctx.wapp.route.assert_any_call('/syslog/last')
		ctx.wapp.route.assert_any_call('/syslog/last/<limit:int>')
		ctx.view.assert_any_call('syslog.html')
		ctx.tpl.data.assert_any_call('syslog')
		assert sorted(d.keys()) == ['limit', 'lvlmap', 'msgs']

def test_limit(testing_webapp):
	wapp = testing_webapp('view')
	with wapp.mock() as ctx:
		d = syslog.index(limit = '3')
		assert d['limit'] == '3'
		d = syslog.index(limit = '-1')
		assert d['limit'] == '0'
		d = syslog.index(limit = 's')
		assert d['limit'] == '0'
