# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import systemd
from _sadm.utils.cmd import callCheck

__all__ = ['deploy']

# run as root at last pass
sumode = 'post'

def deploy(env):
	env.log('newaliases')
	callCheck('newaliases')
	systemd.restart('postfix')
