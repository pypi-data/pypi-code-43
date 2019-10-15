# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['cfgfilter', 'configure']

_options = ('update', 'install', 'remove', 'prune', 'common.enable')

def cfgfilter(env, pcfg, dep):
	dn = env.dist() + '.'
	def pfilter(opt):
		if opt.startswith(dn):
			for n in _options:
				n = '.' + n
				if opt.endswith(n):
					return opt
		return None
	env.settings.merge(pcfg, dep, pfilter)

def configure(env, cfg):
	env.settings.merge(cfg, 'os.pkg', _options)
