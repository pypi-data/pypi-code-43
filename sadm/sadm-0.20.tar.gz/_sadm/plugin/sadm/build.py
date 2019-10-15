# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from hashlib import sha256
from subprocess import call

from _sadm import libdir
from _sadm.deploy import extractor
from _sadm.errors import BuildError
from _sadm.utils import path, builddir

__all__ = ['pre_build', 'build', 'post_build']

#
# pre build
#

def pre_build(env):
	builddir.lock(env)
	_writeSettings(env)

def _writeSettings(env):
	env.log('configure.ini')
	fn = None
	with builddir.create(env, 'configure.ini', meta = True) as fh:
		env.settings.write(fh)
		fn = fh.name
	h = sha256()
	with open(fn, 'rb') as fh:
		h.update(fh.read())
	env.session.set('sadm.configure.checksum', h.hexdigest())

#
# build
#

def build(env):
	if env.session.get('sadm.listen.enable', False):
		env.log('enable sadm-listen')
		_buildListen(env)

def _buildListen(env):
	cfgfiles = (
		(libdir.fpath('listen', 'wsgi', 'uwsgi.ini'),
			path.join(path.sep, 'etc', 'opt', 'sadm', 'listen', 'uwsgi.ini')),
		(libdir.fpath('listen', 'wsgi', 'uwsgi.service'),
			path.join(path.sep, 'etc', 'systemd', 'system', 'sadm-listen.service')),
		(libdir.fpath('listen', 'wsgi', 'apache.conf'),
			path.join(path.sep, 'etc', 'opt', 'sadm', 'listen', 'apache.conf')),
		(libdir.fpath('listen', 'wsgi', 'nginx.conf'),
			path.join(path.sep, 'etc', 'opt', 'sadm', 'listen', 'nginx.conf')),
		(libdir.fpath('listen', 'wsgi', 'lighttpd.conf'),
			path.join(path.sep, 'etc', 'opt', 'sadm', 'listen', 'lighttpd.conf')),
		(libdir.fpath('listen', 'fail2ban', 'filter.d', 'sadm-listen.conf'),
			path.join(path.sep, 'etc', 'fail2ban', 'filter.d', 'sadm-listen.conf')),
	)
	for srcfn, dstfn in cfgfiles:
		env.log("create %s" % dstfn)
		with open(srcfn, 'r') as src:
			with builddir.create(env, dstfn) as dst:
				dst.write(src.read())
#
# post build
#

def post_build(env):
	_saveSession(env)
	_signBuild(env)
	extractor.gen(env)
	builddir.unlock(env)

def _saveSession(env):
	env.debug('session.json')
	with builddir.create(env, 'session.json', meta = True) as fh:
		env.session.dump(fh)

def _signBuild(env):
	sid = env.profile.config.get(env.profile.name(), 'build.sign', fallback = '')
	sid = sid.strip()
	if sid != '':
		env.log("sign id %s" % sid)
		fn = path.normpath(env.build.rootdir()) + '.env'
		env.log("sign env %s" % fn)
		rc = call("gpg --no-tty --yes -u '%s' -sba %s" % (sid, fn), shell = True)
		if rc != 0:
			raise BuildError('build sign using gpg failed')
