# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log, env, deploy

def run(envobj, sumode):
	log.debug("***** RUN %s SUMODE %s *****" % (envobj, sumode))
	rc, _ = env.run('deploy', envobj, 'deploy', cfgfile = deploy.cfgfile, sumode = sumode)
	return rc
