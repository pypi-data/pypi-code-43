# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
from _sadm import log, env
from _sadm.cmd import flags
from _sadm.cmd.deploy import loader
from _sadm.cmd.deploy import deploy
from _sadm.utils import sh

def _getArgs(p, argv):
	subparser = p.add_subparsers(title = 'commands',
		description = 'run `sadm command -h` for more information',
		help = 'description')
	loader.cmdArgs(subparser)
	deploy.cmdArgs(subparser)
	return flags.parse(p, argv)

def main(argv = None):
	if argv is None:
		argv = sys.argv[1:] # pragma: no cover

	sumode = 'not'
	if '--sumode-pre' in argv:
		argv.remove('--sumode-pre')
		sumode = 'pre'
	elif '--sumode-post' in argv:
		argv.remove('--sumode-post')
		sumode = 'post'

	_parser = flags.new('sadm', desc = 'deploy sadm env')
	args = _getArgs(_parser, argv)
	log.debug("deploy %s/%s sumode=%s" % (args.profile, args.env, sumode))

	if sumode == 'not' and sh.getuid() == 0:
		log.error('do not run as root')
		return 9

	try:
		cmd = args.command
	except AttributeError: # pragma: no cover
		log.error('invalid usage')
		_parser.print_usage()
		return 1
	log.debug("dispatch command %s" % cmd)

	if args.command == 'import':
		return loader.main(args)

	return deploy.main(args, sumode)

if __name__ == '__main__':
	sys.exit(main()) # pragma: no cover
