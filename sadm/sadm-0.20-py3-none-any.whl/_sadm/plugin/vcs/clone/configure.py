# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['configure']

def configure(env, cfg):
	if cfg.getboolean('vcs.clone', 'enable', fallback = True):
		for s in cfg.sections():
			if s.startswith('vcs.repo'):
				_configRepo(env, cfg, s)

def _configRepo(env, cfg, sect):
	env.settings.merge(cfg, sect, (
		'type',
		'remote',
		'branch',
		'checkout',
		'path',
		'update',
		'deploy',
	))
