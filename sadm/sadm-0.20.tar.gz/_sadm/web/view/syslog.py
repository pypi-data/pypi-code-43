# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import request
from _sadm import log
from _sadm.web import tpl, syslog
from _sadm.web.app import wapp, view

@wapp.route('/syslog')
@wapp.route('/syslog/last')
@wapp.route('/syslog/last/<limit:int>')
@view('syslog.html')
@tpl.data('syslog')
def index(limit = '100'):
	limit = request.query.get('limit', limit)
	try:
		if int(limit) < 0:
			limit = '0'
	except ValueError:
		limit = '0'
	log.debug("last %s messages" % limit)
	lvlmap = dict()
	for lname, lid in syslog._LVLMAP.items():
		lvlmap[lid] = lname
	return {
		'limit': limit,
		'msgs': syslog.last(int(limit)),
		'lvlmap': lvlmap,
	}
