# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import systemd
from _sadm.utils.sh import makedirs, chmod, chown

__all__ = ['deploy']

# run as root at last pass
sumode = 'post'

def deploy(env):
	dbdir = env.settings.get('service.munin', 'db.dir')
	makedirs(dbdir, exists_ok = True)
	chmod(dbdir, 0o750)

	dbuser = env.settings.get('service.munin', 'dbdir.user')
	dbgroup = env.settings.get('service.munin', 'dbdir.group')
	chown(dbdir, user = dbuser, group = dbgroup)

	env.log("dbdir %s (%s:%s)" % (dbdir, dbuser, dbgroup))

	if systemd.status('cron') != 0:
		systemd.restart('cron')

	if systemd.status('munin') != 0:
		systemd.restart('munin')
