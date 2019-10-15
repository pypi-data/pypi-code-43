# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path
from pytest import raises

from _sadm.errors import EnvError, ServiceError
from _sadm.plugin import service

def test_defaults(testing_env):
	env = testing_env(name = 'service', profile = 'plugin')
	assert env.name() == 'service'
	assert env.profile.name() == 'plugin'
	assert env.cfgfile() == path.join('service', 'config.ini')
	assert env.settings.sections() == []

def test_configure(testing_env):
	env = testing_env(name = 'service', profile = 'plugin')
	env.configure()
	assert sorted(env.settings.sections()) == ['sadm', 'service']
	assert env.settings.get('service', 'config.dir') == 'service'
	assert env.settings.getlist('service', 'enable') == ()

def test_enable(testing_env):
	env = testing_env(name = 'service', profile = 'plugin')
	env.configure(cfgfile = path.join('service', 'config-testing.ini'))
	assert env.settings.getlist('service', 'enable') == ('testing',)

def test_enable_error(testing_env):
	env = testing_env(name = 'service', profile = 'plugin')
	with raises(EnvError, match = r'config\.ini file not found'):
		env.configure(cfgfile = path.join('service', 'config-nosvc.ini'))

def test_config_error(testing_env):
	env = testing_env(name = 'service', profile = 'plugin')
	with raises(ServiceError, match = 'Source contains parsing errors'):
		env.configure(cfgfile = path.join('service', 'config-error.ini'))
