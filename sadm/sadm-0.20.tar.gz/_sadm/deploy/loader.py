# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

from _sadm import log, cfg, deploy
from _sadm.utils import path, sh
from _sadm.utils.cmd import call

def loadenv(filename):
	envfn = path.abspath(filename)
	log.msg("%s: load" % envfn)
	rc = _check(envfn)
	if rc != 0:
		return rc
	if path.isfile(envfn + '.asc'):
		rc = _verify(envfn)
		if rc != 0:
			return rc
	rc = call("sha256sum -c %s" % envfn)
	if rc != 0:
		log.error('env checksum failed!')
		return rc
	_importenv(envfn)
	return 0

def _check(envfn):
	if not envfn.endswith('.env'):
		log.error("invalid file name: %s" % envfn)
		return 1
	env = path.basename(envfn)[:-4]
	config = cfg.new(deploy.cfgfile)
	if not env in config.listEnvs('deploy'):
		log.error("%s env not found" % env)
		return 2
	return 0

def _verify(envfn):
	rc = call("gpg --no-tty --no --verify %s.asc %s 2>/dev/null" % (envfn, envfn))
	if rc == 0:
		log.msg("%s: OK" % envfn)
	else:
		log.error('env signature verify failed!')
	return rc

def _importenv(envfn):
	srcfn = envfn[:-4]
	rootdir = path.dirname(path.dirname(envfn))
	deploydir = path.join(rootdir, 'deploy')
	envdir = path.join(deploydir, path.basename(srcfn))
	if path.isdir(envdir):
		sh.rmtree(envdir)
	sh.makedirs(envdir)
	sh.chmod(envdir, 0o0700)
	log.msg("%s.zip: unpack" % srcfn)
	sh.unpack_archive(srcfn + '.zip', extract_dir = envdir, format = 'zip')
