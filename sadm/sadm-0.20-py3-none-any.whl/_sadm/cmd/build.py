# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys
from _sadm import log, env
from _sadm.cmd import flags

def _getArgs(argv):
	parser = flags.new('sadm-build', desc = 'build sadm env')
	return flags.parse(parser, argv)

def main(argv = None):
	if argv is None:
		argv = sys.argv[1:] # pragma: no cover
	args = _getArgs(argv)
	log.debug("build %s/%s" % (args.profile, args.env))
	rc, _ = env.run(args.profile, args.env, 'build')
	return rc

if __name__ == '__main__':
	sys.exit(main()) # pragma: no cover
