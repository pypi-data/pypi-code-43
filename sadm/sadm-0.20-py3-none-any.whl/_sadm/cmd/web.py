# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

from _sadm import log, version
from _sadm.cmd import flags
from _sadm.web import app, syslog

def _getArgs(argv):
	p = flags.new('sadm-web', desc = 'sadm web interface')
	# ~ p.add_argument('--address', help = 'bind to ip address (localhost)',
		# ~ metavar = 'address', default = 'localhost')
	p.add_argument('--port', help = 'bind to tcp port (3478)',
		metavar = 'number', type = int, default = 3478)
	return flags.parse(p, argv)

def main(argv = None):
	if argv is None:
		argv = sys.argv[1:] # pragma: no cover
	args = _getArgs(argv)
	log.info("sadm-web v%s" % version.get())
	log.msg("http://%s:%d/" % ('localhost', args.port))
	syslog.init()
	app.run('localhost', args.port, args.debug)
	syslog.close()
	log.msg('done!')
	return 0

if __name__ == '__main__':
	sys.exit(main()) # pragma: no cover
