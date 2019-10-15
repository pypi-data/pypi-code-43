# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from collections import deque
from os import devnull

# TODO: move pwd package funcs to utils so we can mock it for tests
from pwd import getpwnam

from _sadm.utils.cmd import call, callOutput

__all__ = ['check']

def check(env):
	diff = deque()
	_checkGroups(diff, env)
	_checkUsers(diff, env)
	return diff

def _checkGroups(diff, env):
	if not env.settings.has_section('os.group'):
		return
	for group in env.settings['os.group']:
		gid = env.settings.getint('os.group', group)
		rc = call("getent group %s >%s" % (group, devnull))
		if rc == 2:
			diff.append(('group', group, gid))
			env.warn("%d %s not found" % (gid, group))
		elif rc == 0:
			env.log("%d %s OK" % (gid, group))
		else:
			raise env.error("getent group command failed: %d" % rc)

def _checkUsers(diff, env):
	for user in env.settings['os.user']:
		uid = env.settings.getint('os.user', user)
		try:
			info = getpwnam(user)
		except KeyError:
			diff.append(('user', user, uid))
			env.warn("%d %s not found" % (uid, user))
			groups = env.settings.getlist("os.user.%s" % user, 'groups', fallback = [])
			for g in groups:
				diff.append(('user.group', user, g))
		else:
			if info.pw_uid != uid:
				env.warn("%d %s uid %d does not match" % (uid, user, info.pw_uid))
			else:
				env.log("%d %s OK" % (uid, user))
				groups = env.settings.getlist("os.user.%s" % user, 'groups', fallback = [])
				_checkUserGroups(diff, env, user, groups)

def _checkUserGroups(diff, env, user, groups):
	env.debug("check %s user groups %s" % (user, groups))
	okAll = True
	for g in groups:
		cmd = "getent group %s | cut -d ':' -f 4 | tr ',' ' '" % g
		rc, output = callOutput(cmd)
		if rc == 0:
			ok = False
			for n in output.split(' '):
				n = n.strip()
				if n == user:
					ok = True
					break
			if not ok:
				diff.append(('user.group', user, g))
				okAll = False
		elif rc == 2:
			env.warn("os group %s not found" % g)
	if okAll:
		env.log("user %s groups OK" % user)
