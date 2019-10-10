# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle
from configparser import ConfigParser, ExtendedInterpolation

from _sadm import libdir, log, version
from _sadm.listen import errors, handlers
from _sadm.utils import path

__all__ = ['wapp', 'config', 'init']

_wappcfg = libdir.fpath('listen', 'wapp.conf')
_cfgfn = path.join(path.sep, 'etc', 'opt', 'sadm', 'listen.cfg')

wapp = bottle.Bottle()
config = None

def _newConfig(fn):
	c = ConfigParser(
		defaults = None,
		allow_no_value = False,
		delimiters = ('=',),
		comment_prefixes = ('#',),
		strict = True,
		interpolation = ExtendedInterpolation(),
		default_section = 'default',
	)
	with open(fn, 'r') as fh:
		c.read_file(fh)
	return c

def init(cfgfn = _cfgfn):
	global config

	wapp.config.load_config(_wappcfg)
	bottle.TEMPLATE_PATH = []

	config = _newConfig(cfgfn)
	log.init(config.get('sadm', 'log', fallback = 'error'))
	log.debug(version.string('sadm-listen'))
	log.debug("read config %s" % cfgfn)

	rmplugins = [p.strip() for p in wapp.config.get('plugins.uninstall', '').split(' ')]
	for p in rmplugins:
		if p != '':
			log.debug("plugin uninstall %s" % p)
			wapp.uninstall(p)

	errors.init(wapp)
	handlers.init(wapp, config)

	log.debug("loaded handlers %s" % [r.name for r in wapp.routes])
	return wapp
