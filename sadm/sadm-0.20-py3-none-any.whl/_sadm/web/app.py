# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle

from _sadm import libdir

__all__ = ['wapp', 'view', 'run']

_cfgfn = libdir.fpath('web', 'app.conf')
_htmldir = libdir.fpath('web', 'html')
_staticdir = libdir.fpath('web', 'static')

bottle.TEMPLATE_PATH = [_htmldir]
view = bottle.view

wapp = bottle.Bottle()
wapp.config.load_config(_cfgfn)

@wapp.route('/static/<filename:path>')
def _static(filename):
	return bottle.static_file(filename, root = _staticdir, download = False)

def run(host, port, debug):
	import _sadm.web.load # load views
	wapp.run(host = host, port = port, reloader = debug,
		quiet = not debug, debug = debug)
