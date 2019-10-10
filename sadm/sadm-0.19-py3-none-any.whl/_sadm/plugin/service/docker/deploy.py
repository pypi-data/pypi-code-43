# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import systemd

__all__ = ['deploy']

sumode = 'post'

def deploy(env):
	for s in env.settings.sections():
		if s.startswith('docker-compose:'):
			name = s.replace('docker-compose:', '', 1).strip()
			cfg = env.settings[s]
			_composeConfigure(env, name, cfg)

def _composeConfigure(env, name, cfg):
	env.log("docker-compose configure %s" % name)
	enable = cfg.getboolean('systemd.enable', fallback = True)
	service = "docker-compose-%s.service" % name
	if enable:
		systemd.enable(service)
		if cfg.getboolean('start', fallback = True):
			systemd.start(service)
