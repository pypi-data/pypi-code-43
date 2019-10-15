# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sqlite3

from bottle import __version__ as bottle_version
from datetime import date
from sys import version as python_version

from _sadm import log
from _sadm.web import tpl
from _sadm.web.app import wapp, view

@wapp.route('/about')
@view('about.html')
@tpl.data('about')
def about():
	log.debug("about")
	return {
		'pythonVersion': python_version,
		'bottleVersion': bottle_version,
		'sqliteVersion': "%s" % sqlite3.version,
		'sqliteLibVersion': "%s" % sqlite3.sqlite_version,
		'curyear': str(date.today().year),
	}
