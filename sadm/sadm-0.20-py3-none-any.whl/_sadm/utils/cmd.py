# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import subprocess

from os import environ

from _sadm.errors import CommandError

__all__ = ['call', 'callCheck']

PROC_TTL = 900 # 15 minutes

class _ProcMan(object):

	def __init__(self):
		self.call = subprocess.call
		self.check_call = subprocess.check_call

	def _run(self, cmd, getoutput = False, check = False, **kwargs):
		shell = False
		if isinstance(cmd, str):
			shell = True
		return subprocess.run(cmd, capture_output = getoutput, timeout = PROC_TTL,
			check = check, shell = shell, **kwargs)

	def callOutput(self, cmd):
		p = self._run(cmd, getoutput = True, encoding = 'utf-8')
		return (p.returncode, p.stdout)

proc = _ProcMan()

def call(cmd, env = None, timeout = None):
	shell = False
	if isinstance(cmd, str):
		shell = True
	return proc.call(cmd, env = env, shell = shell, timeout = timeout)

def callOutput(cmd):
	return proc.callOutput(cmd)

def callCheck(cmd, env = None):
	if env is None:
		env = environ.copy()
	shell = False
	if isinstance(cmd, str):
		shell = True
	cmderr = None
	try:
		proc.check_call(cmd, env = env, shell = shell)
	except subprocess.CalledProcessError as err:
		cmderr = str(err)
	except KeyboardInterrupt:
		pass
	if cmderr is not None:
		raise CommandError(cmderr)
