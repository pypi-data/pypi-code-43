# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log, cfg
from _sadm.cmd import flags
from _sadm.deploy import cmd, cfgfile
from _sadm.env import Env
from _sadm.utils import sh, path
from _sadm.utils.cmd import call

def cmdArgs(parser):
	p = parser.add_parser('deploy', help = 'deploy sadm.env')
	p.set_defaults(command = 'deploy')

def main(args, sumode):
	log.debug("deploy %s sumode=%s" % (args.env, sumode))
	if sumode == 'not':
		dn = path.join('~', '.local', 'sadm', 'deploy')
		sh.makedirs(dn, mode = 0o750, exists_ok = True)
		with sh.lockd(dn):
			env = Env('deploy', args.env, cfg.new(cfgfile = cfgfile))
			for rc in (
				_sumode(env, 'pre'),
				_usermode(env),
				_sumode(env, 'post'),
			):
				if rc != 0:
					return rc
	else:
		return cmd.run(args.env, sumode)

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
	return cmd.run(env, 'not')
