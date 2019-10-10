# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from contextlib import contextmanager

from _sadm.utils import sh
from _sadm.utils.cmd import callCheck
from _sadm.utils import path as fpath

__all__ = ['clone', 'checkout', 'pull', 'deploy']

_configDone = False

def _configure():
	global _configDone
	if _configDone:
		return
	sshcmd = ('ssh',
		'-o', 'UserKnownHostsFile=/dev/null',
		'-o', 'StrictHostKeyChecking=no',
		'-o', 'BatchMode=yes',
	)
	cmd = ['git', 'config', '--global', 'core.sshCommand', ' '.join(sshcmd)]
	callCheck(cmd)
	_configDone = True

def clone(path, remote, branch):
	_configure()
	cmd = ['git', 'clone', '-b', branch, remote, path]
	callCheck(cmd)

@contextmanager
def _repoDir(path):
	_configure()
	oldwd = sh.getcwd()
	try:
		sh.chdir(path)
		yield
	finally:
		sh.chdir(oldwd)

def checkout(path, commit):
	with _repoDir(path):
		callCheck(['git', 'checkout', commit])

def pull(path):
	with _repoDir(path):
		callCheck(['git', 'pull'])

_deployScripts = ('install.sh', 'build.sh',  'check.sh', 'deploy.sh')

def deploy(path):
	with _repoDir(path):
		if fpath.isdir('.sadm'):
			for sn in _deployScripts:
				script = fpath.join('.', '.sadm', sn)
				if fpath.isfile(script):
					callCheck(['/bin/sh', script])
