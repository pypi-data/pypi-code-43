# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['configure']

def configure(env, cfg):
	env.settings.merge(cfg, 'network.fail2ban', (
		'config.dir',
		'config.destdir',
		'jail.disable',
		'jail.enable',
	))
