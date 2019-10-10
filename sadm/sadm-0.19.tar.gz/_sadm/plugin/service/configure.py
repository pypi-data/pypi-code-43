# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import libdir
from _sadm.service import Service
from _sadm.utils import path

__all__ = ['configure']

def configure(env, cfg):
	env.settings.merge(cfg, 'service', (
		'config.dir',
		'enable',
	))
	_loadEnabled(env)

def _loadEnabled(env):
	fn = 'config.ini'
	cfgdir = env.settings.get('service', 'config.dir', fallback = 'service')
	for s in env.settings.getlist('service', 'enable'):
		env.log("enable %s" % s)
		libfn = libdir.fpath('service', s, fn)
		libok = _loadConfig(env, libfn)
		sfn = env.assets.rootdir(cfgdir, s, fn)
		sok = _loadConfig(env, sfn)
		if not sok and not libok:
			raise env.error("%s file not found" % sfn)

def _loadConfig(env, fn):
	ok = False
	env.debug("load %s" % fn)
	if path.isfile(fn):
		Service(fn)
		ok = True
	else:
		env.debug("%s file not found" % fn)
	return ok
