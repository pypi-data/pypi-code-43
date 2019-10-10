# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import path, systemd

__all__ = ['deploy']

_cfgfn = path.join(path.sep, 'etc', 'opt', 'sadm', 'listen.cfg')

# run as root at first pass
sumode = 'pre'

def deploy(env):
	# TODO: read config and check if it is enabled
	if path.isfile(_cfgfn):
		env.info("%s found" % _cfgfn)
		if systemd.status('sadm-listen', 'is-enabled') != 0:
			env.log('sadm-listen enable')
			systemd.enable('sadm-listen')
		if systemd.status('sadm-listen') != 0:
			env.log('sadm-listen restart')
			systemd.restart('sadm-listen')
