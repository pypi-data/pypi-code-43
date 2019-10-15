# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.web.view import profile

def test_index(testing_webapp):
	wapp = testing_webapp('view')
	with wapp.mock() as ctx:
		d = profile.index()
		ctx.wapp.route.assert_any_call('/profile')
		ctx.view.assert_any_call('profile.html')
		ctx.tpl.data.assert_any_call('profile')
		assert sorted(d.keys()) == ['profiles']
