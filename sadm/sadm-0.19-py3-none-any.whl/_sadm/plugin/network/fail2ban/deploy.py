# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import path, systemd

__all__ = ['deploy']

# run as root at last pass
sumode = 'post'

def deploy(env):
	destdir = env.settings.get('network.fail2ban', 'config.destdir')
	jdisable = env.settings.getlist('network.fail2ban', 'jail.disable')
	for jn in jdisable:
		fn = path.join(destdir, 'jail.d', jn + '.conf')
		if path.isfile(fn):
			env.log("remove %s" % fn)
			path.unlink(fn)
	env.log("restart")
	systemd.restart('fail2ban')
