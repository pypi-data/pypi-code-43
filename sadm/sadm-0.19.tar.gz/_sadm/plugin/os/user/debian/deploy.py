# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils.cmd import callCheck as call

from .check import check

__all__ = ['deploy']

def deploy(env):
	env.log('os user')
	for diff in check(env):
		typ = diff[0]
		if typ == 'group':
			_addGroup(env, diff[1], diff[2])
		elif typ == 'user':
			_addUser(env, diff[1], diff[2])
		elif typ == 'user.group':
			_addUserGroup(env, diff[1], diff[2])
		else:
			raise RuntimeError("unknown os.user check type: %s" % typ)

def _addGroup(env, group, gid):
	call(['groupadd', '-g', str(gid), group])
	env.log("%d %s group created" % (gid, group))

def _addUser(env, user, uid):
	cmd = ['useradd', '-m', '-U', '-u', str(uid)]

	fullname = env.settings.get("os.user.%s" % user, 'fullname', fallback = '').strip()
	if fullname != '':
		cmd.append('-c')
		cmd.append("'%s'" % fullname)

	shell = env.settings.get("os.user.%s" % user, 'shell', fallback = '/bin/bash').strip()
	cmd.append('-s')
	cmd.append(shell)

	cmd.append(user)
	call(cmd)
	env.log("%d %s user created" % (uid, user))

def _addUserGroup(env, user, group):
	call(['usermod', '-a', '-G', group, user])
	env.log("%s user added to %s group" % (user, group))
