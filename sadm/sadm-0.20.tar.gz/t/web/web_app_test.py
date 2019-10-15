# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from unittest.mock import Mock

from _sadm.web import app

def test_static(testing_webapp):
	wapp = testing_webapp('app')
	with wapp.mock() as ctx:
		bottle = app.bottle
		_staticdir = app._staticdir
		try:
			app.bottle = Mock()
			app._staticdir = '/opt/src/sadm/web/static'
			app._static('testing.txt')
			app.bottle.static_file.assert_called_once_with('testing.txt',
				download = False, root = '/opt/src/sadm/web/static')
		finally:
			del app.bottle
			app.bottle = bottle
			del app._staticdir
			app._staticdir = _staticdir
