# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log, cfg
from _sadm.cmd import flags
from _sadm.deploy import cmd, cfgfile
from _sadm.env import Env
from _sadm.utils import sh, path
from _sadm.utils.cmd import call

class CmdError(Exception):
	def __init__(self, code):
		self.code = code

def cmdArgs(parser):
	p = parser.add_parser('deploy', help = 'deploy sadm.env')
	p.set_defaults(command = 'deploy')

def main(args, sumode):
	log.debug("deploy %s sumode=%s" % (args.env, sumode))
	if sumode == 'not':
		config = cfg.new(cfgfile = cfgfile)
		dn = config.get('deploy', 'rundir',
			fallback = path.join('~', '.local', 'sadm', 'deploy'))
		sh.makedirs(dn, mode = 0o750, exists_ok = True)
		with sh.lockd(dn):
			env = Env('deploy', args.env, config)
			try:
				_check(_sumode(env, 'pre'))
				_check(_usermode(env))
				_check(_sumode(env, 'post'))
			except CmdError as err:
				return err.code
	else:
		return cmd.run(args.env, sumode)
	return 39

def _check(rc):
	if rc != 0:
		raise CmdError(rc)

def _sumode(env, step):
	sumode = '-'.join(['--sumode', step])
	log.debug("call sumode %s" % sumode)
	sudo = env.profile.config.get('deploy', 'sudo.command')
	cmd = sudo.strip().split()
	cmd.extend(flags.cmdline.split())
	cmd.append(sumode)
	log.debug("sumode cmd %s" % ' '.join(cmd))
	return call(cmd)

def _usermode(env):
	return cmd.run(env, 'user')
