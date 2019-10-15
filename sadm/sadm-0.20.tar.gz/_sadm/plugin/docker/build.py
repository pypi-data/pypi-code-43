# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import systemd

__all__ = ['build']

def build(env):
	for s in env.settings.sections():
		if s.startswith('docker-compose:'):
			name = s.replace('docker-compose:', '', 1).strip()
			cfg = env.settings[s]
			_composeConfigure(env, name, cfg)

def _composeConfigure(env, name, cfg):
	env.log("docker-compose %s" % name)
	enable = cfg.getboolean('systemd.enable', fallback = True)
	if enable:
		spath = cfg.get('path', fallback = '')
		if spath == '':
			raise env.error("docker-compose:%s path is empty" % name)
		tpldat = {
			'serviceName': name,
			'servicePath': spath,
			'serviceUser': cfg.get('user', fallback = 'sadm'),
			'serviceGroup': cfg.get('group', fallback = 'sadm'),
		}
		systemd.configure(env, 'docker-compose', 'service', name, tpldat)
