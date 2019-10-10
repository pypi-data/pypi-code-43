# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils.vcs import git

from .check import check

__all__ = ['deploy']

def deploy(env):
	status = check(env)
	for st, name, typ, repo in status:
		if st == 'MISS':
			_cloneRepo(env, name, typ, repo)
		else:
			_updateRepo(env, name, typ, repo)
		_deployRepo(env, name, typ, repo)

def _cloneRepo(env, name, typ, repo):
	env.log("clone %s repo %s" % (typ, name))
	if typ == 'git':
		_gitClone(env, name, repo)

def _gitClone(env, name, repo):
	git.clone(repo['path'], repo['remote'], repo['branch'])
	if repo['checkout'] != '':
		git.checkout(repo['path'], repo['checkout'])

def _updateRepo(env, name, typ, repo):
	if not repo['update']:
		return
	env.log("update %s repo %s" % (typ, name))
	if typ == 'git':
		git.pull(repo['path'])

def _deployRepo(env, name, typ, repo):
	if not repo['deploy']:
		return
	env.log("deploy %s repo %s" % (typ, name))
	if typ == 'git':
		git.deploy(repo['path'])
