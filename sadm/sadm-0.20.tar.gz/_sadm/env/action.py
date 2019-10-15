# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from time import strftime, time

from _sadm.errors import PluginError

__all__ = ['run']

_validAction = {
	'build': True,
	'deploy': True,
}

def run(env, action, sumode = 'user'):
	_start = time()
	env.info("%s start %s" % (action, strftime('%c %z')))
	env.log("%s %s" % (env.profile.config.name(), env.profile.config.filename()))
	try:
		if not _validAction.get(action, False):
			raise env.error("invalid action %s" % action)
		with env.lock() as env:
			env.configure()
			_runPreAction(env, action, sumode)
			_runAction(env, action, sumode = sumode)
			_runPostAction(env, action, sumode)
			env.report(action, startTime = _start)
	finally:
		env.info("%s end %s" % (action, strftime('%c %z')))

def _runAction(env, action, cmd = None, force = False, revert = False, sumode = 'user'):
	if cmd is None:
		cmd = action
	for p in env.plugins(action, revert = revert):
		if p.sumode != sumode:
			env.debug("%s sumode exclude %s %s" % (sumode, p.name, cmd))
			continue
		if hasattr(p.mod, cmd):
			func = getattr(p.mod, cmd)
			tag = "%s.%s" % (cmd, p.name)
			env.start(tag)
			func(env)
			env.end(tag)
		else:
			env.debug("%s plugin no action %s" % (p.name, cmd))
			if force:
				raise PluginError("%s plugin no action %s" % (p.name, cmd))

def _runPreAction(env, action, sumode):
	_runAction(env, action, cmd = "pre_%s" % action, sumode = sumode)

def _runPostAction(env, action, sumode):
	_runAction(env, action, cmd = "post_%s" % action, revert = True, sumode = sumode)
