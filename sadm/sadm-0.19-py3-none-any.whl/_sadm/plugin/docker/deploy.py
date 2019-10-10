# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import sh, cmd

__all__ = ['deploy']

def deploy(env):
	for s in env.settings.sections():
		if s.startswith('docker-compose:'):
			name = s.replace('docker-compose:', '', 1).strip()
			cfg = env.settings[s]
			_composeBuild(env, name, cfg)

def _composeBuild(env, name, cfg):
	env.log("docker-compose build %s" % name)
	if cfg.getboolean('build', fallback = True):
		workdir = cfg.get('path')
		oldwdir = sh.getcwd()
		try:
			sh.chdir(workdir)
			_composeEnv(env, name, cfg)
			cmd.callCheck(['docker-compose', 'build'])
		finally:
			sh.chdir(oldwdir)

def _composeEnv(env, name, cfg):
	content = cfg.get('env', fallback = '')
	data = []
	for line in content.splitlines():
		line = line.strip()
		if line != '' and not line.startswith('#'):
			data.append(line)
	if data:
		envfn = cfg.get('env.file', fallback = '.env')
		env.log("docker-compose %s %s" % (name, envfn))
		with open(envfn, 'w') as fh:
			fh.write('\n'.join(data))
			fh.write('\n')
