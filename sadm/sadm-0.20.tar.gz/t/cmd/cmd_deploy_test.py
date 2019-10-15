# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from pytest import raises

from _sadm.cmd import deploy
from _sadm.errors import ProfileError

def test_usage_error(testing_cmd):
	cmd = testing_cmd(env = None)
	with cmd.mock('usage_error'):
		with raises(SystemExit) as err:
			deploy.main(argv = ['invalid_command'])
			assert isinstance(err, SystemExit)
			assert err.code == 2

def test_config_notfound(testing_cmd):
	cmd = testing_cmd(cfgfile = 'no-deploy.cfg', env = None)
	with cmd.mock('config_notfound'):
		with raises(ProfileError, match = 'no-deploy.cfg file not found'):
			deploy.main(argv = ['deploy'])

def test_pre_error(testing_cmd):
	cmd = testing_cmd(deploy = True)
	with cmd.mock('pre_error'):
		rc = deploy.main(argv = ['deploy'])
		assert rc == 128

def test_sumode_pre(testing_cmd):
	cmd = testing_cmd(deploy = True)
	with cmd.mock('sumode_pre'):
		rc = deploy.main(argv = ['deploy', '--sumode-pre'])
		assert rc == 0

def test_post_error(testing_cmd):
	cmd = testing_cmd(deploy = True)
	with cmd.mock('post_error'):
		rc = deploy.main(argv = ['deploy'])
		assert rc == 128

def test_sumode_post(testing_cmd):
	cmd = testing_cmd(deploy = True)
	with cmd.mock('sumode_post'):
		rc = deploy.main(argv = ['deploy', '--sumode-post'])
		assert rc == 0

def test_root_error(testing_cmd):
	cmd = testing_cmd(deploy = True)
	with cmd.mock('root_error'):
		rc = deploy.main(argv = ['deploy'])
		assert rc == 9

def test_main(testing_cmd):
	cmd = testing_cmd(deploy = True)
	with cmd.mock():
		rc = deploy.main(argv = ['deploy'])
		assert rc == 39

def test_import(testing_cmd):
	cmd = testing_cmd()
	with cmd.mock('import'):
		rc = deploy.main(argv = ['import', 'testing.env'])
		assert rc == 0

def test_import_invalid_file(testing_cmd):
	cmd = testing_cmd()
	with cmd.mock('import_invalid_file'):
		rc = deploy.main(argv = ['import', 'env.file'])
		assert rc == 1

def test_import_noenv(testing_cmd):
	cmd = testing_cmd()
	with cmd.mock('import_noenv'):
		rc = deploy.main(argv = ['import', 'noenv.env'])
		assert rc == 2

def test_import_cksum_error(testing_cmd):
	cmd = testing_cmd()
	with cmd.mock('import_cksum_error'):
		rc = deploy.main(argv = ['import', 'testing.env'])
		assert rc == 9

def test_import_verify(testing_cmd):
	cmd = testing_cmd()
	with cmd.mock('import_verify'):
		rc = deploy.main(argv = ['import', 'testing.env'])
		assert rc == 9

def test_import_verify_error(testing_cmd):
	cmd = testing_cmd()
	with cmd.mock('import_verify_error'):
		rc = deploy.main(argv = ['import', 'testing.env'])
		assert rc == 8
