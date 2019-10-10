# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path

from _sadm.configure import pluginsList, getPlugin
from _sadm.env.settings import Settings

# load plugins
import _sadm.plugin.load

__all__ = ['configure']

_cfgfilter = {}

def configure(env, cfgfile = None):
	if cfgfile is None:
		cfgfile = env.cfgfile()
	fn = cfgfile
	env.log("%s" % fn)
	env.start('configure')
	_getcfg(env, fn)
	env.end('configure')

def _getcfg(env, fn):
	runconfigure = True
	cfg = Settings()
	with env.assets.open(fn) as fh:
		cfg.read_file(fh)
	n = cfg.get('sadmenv', 'name', fallback = None)
	if n is None:
		# env config
		n = cfg.get('sadm', 'env', fallback = None)
	else:
		# deploy mode
		runconfigure = False
	# check env/config names match
	if n != env.name():
		raise env.error("%s invalid config name from %s file" % (n, env.assets.rootdir(fn)))
	if runconfigure:
		# env config
		_load(env, cfg)
	else:
		# deploy mode
		with env.assets.open(fn) as fh:
			env.settings.read_file(fh)

def _load(env, cfg, forcePlugins = None):
	env.debug("registered plugins %s" % ','.join([p for p in pluginsList()]))
	if forcePlugins is None:
		forcePlugins = {}
		for p in env.profile.config.listPlugins(env.profile.name()):
			forcePlugins[p] = True
	env.debug("plugins force enable: %s" % ','.join([p for p in forcePlugins.keys()]))
	for p in pluginsList():
		ena = cfg.has_section(p)
		forceEna = forcePlugins.get(p, False)
		if ena or forceEna:
			env.debug("%s plugin enabled" % p)
			_pluginConfigure(env, cfg, p)
		else:
			env.debug("%s plugin disabled" % p)

def _pluginConfigure(env, cfg, n):
	p = getPlugin(n, 'configure')
	_initPlugin(env, p, cfg)
	env.log(p.name)
	p.mod.configure(env, cfg)
	if hasattr(p.mod, 'cfgfilter'):
		env.debug("plugin %s register cfgfilter" % p.name)
		_cfgfilter[p.name] = getattr(p.mod, 'cfgfilter')

def _initPlugin(env, p, cfg):
	env.debug("init %s" % p.config)
	pcfg = Settings()
	with open(p.config, 'r') as fh:
		pcfg.read_file(fh)
	# load plugin deps
	for dep in pcfg.plugins():
		pfilter = _cfgfilter.get(dep, None)
		if pfilter is not None:
			pfilter(env, pcfg, dep)
	# merge plugin config to env settings
	if not env.settings.has_section(p.name):
		env.settings.add_section(p.name)
	for opt, val in pcfg.items(p.name, raw = True):
		env.settings[p.name][opt] = val
