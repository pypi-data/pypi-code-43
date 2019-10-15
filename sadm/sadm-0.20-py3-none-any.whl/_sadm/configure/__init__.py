# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque, namedtuple
from importlib import import_module
from os import path

from _sadm import log
from _sadm.errors import PluginError

__all__ = ['register', 'getPlugin', 'pluginList']

_reg = {}
_order = deque()

Plugin = namedtuple('Plugin', ('name', 'fullname', 'config', 'meta', 'mod', 'sumode'))

def register(name, filename):
	if name.startswith('_sadmtest.'):
		n = name.replace('_sadmtest.plugin.', '')
	else:
		n = name.replace('_sadm.plugin.', '')
	if _reg.get(n, None) is not None:
		raise RuntimeError("plugin %s already registered" % name)
	srcdir = path.realpath(path.dirname(filename))
	cfgfn = path.join(srcdir, 'config.ini')
	metafn = path.join(srcdir, 'meta.json')
	_reg[n] = {
		'name': name,
		'srcdir': srcdir,
		'config': cfgfn,
		'meta': metafn,
	}
	_order.append(n)

def pluginsList(revert = False):
	_l = list
	if revert:
		_l = reversed
	for p in _l(_order):
		yield p

def getPlugin(name, action):
	p = _reg.get(name, None)
	if p is None:
		raise PluginError("%s plugin not found" % name)
	pkg = p['name']
	try:
		mod = import_module("%s.%s" % (pkg, action))
	except ImportError as err:
		log.debug("%s: %s" % (type(err), err))
		raise PluginError("%s.%s: %s" % (name, action, err))
	except Exception as err:
		raise PluginError("%s %s: %s" % (name, action, err))
	sumode = 'user'
	if action == 'deploy':
		if hasattr(mod, 'sumode'):
			sumode = getattr(mod, 'sumode')
	return Plugin(
		name = name,
		fullname = pkg,
		config = p['config'],
		meta = p['meta'],
		mod = mod,
		sumode = sumode,
	)
