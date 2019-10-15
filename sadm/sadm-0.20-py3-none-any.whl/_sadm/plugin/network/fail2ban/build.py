# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import builddir, path

__all__ = ['build']

def build(env):
	cfgdir = env.assets.name(env.settings.get('network.fail2ban', 'config.dir'))
	destdir = env.settings.get('network.fail2ban', 'config.destdir')
	_jailLocalConf(env, cfgdir, destdir)
	_jailEnable(env, cfgdir, destdir)
	_syncConf(env, cfgdir, destdir)

def _jailLocalConf(env, cfgdir, destdir):
	fn = 'jail.local'
	if env.assets.isfile(cfgdir, fn):
		src = env.assets.name(cfgdir, fn)
		dst = path.join(destdir, fn)
		env.log("copy %s" % dst)
		builddir.copy(env, src, dst)

def _jailEnable(env, cfgdir, destdir):
	jenable = env.settings.getlist('network.fail2ban', 'jail.enable')
	if env.assets.isdir(cfgdir, 'jail.d'):
		for jn in jenable:
			src = env.assets.name(cfgdir, 'jail.d', jn + '.conf')
			dst = path.join(destdir, 'jail.d', jn + '.conf')
			env.log("enable %s" % dst)
			builddir.copy(env, src, dst)

def _syncConf(env, cfgdir, destdir):
	for dn in ('action.d', 'fail2ban.d', 'filter.d'):
		if env.assets.isdir(cfgdir, dn):
			src = env.assets.name(cfgdir, dn)
			dst = path.join(destdir, dn)
			env.log("sync %s" % dst)
			builddir.sync(env, src, dst)
