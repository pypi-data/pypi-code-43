#!/usr/bin/env python3

# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import sys

from _sadm import listen, libdir
from _sadm.cmd import flags
from _sadm.utils import path, sh
from _sadm.utils.cmd import callCheck

def bottle():
	return listen.start()

def uwsgi():
	cmd = [
		'uwsgi',
		'--need-plugin', 'python3',
		'--set-ph', "sadm-home=%s" % sys.exec_prefix,
		'--touch-reload', path.join(path.sep, 'etc', 'opt', 'sadm', 'listen.cfg'),
		'--touch-reload', libdir.fpath('listen', 'wsgi', 'uwsgi.ini'),
		'--safe-pidfile', path.join(path.sep, 'tmp', 'sadm.listen.uwsgi.pid'),
		'--ini', libdir.fpath('listen', 'wsgi', 'uwsgi.ini'),
	]
	callCheck(cmd)
	return 0

if __name__ == '__main__':
	if '--bottle' in sys.argv:
		sys.exit(bottle())
	else:
		sys.exit(uwsgi())
