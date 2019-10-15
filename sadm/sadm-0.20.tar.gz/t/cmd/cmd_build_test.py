# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.cmd import build

def test_main(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('build_main'):
		rc = build.main(argv = ['--profile', 'cmd', '--env', 'testing'])
		assert rc == 0

def test_error(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('build_error'):
		rc = build.main(argv = ['--profile', 'cmd', '--env', 'noenv'])
		assert rc == 1
