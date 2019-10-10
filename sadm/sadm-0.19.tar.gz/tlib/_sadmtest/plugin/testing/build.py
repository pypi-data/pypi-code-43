# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.utils import builddir

def build(env):
	env.log('build')
	testing_error = env.settings.get('testing', 'testing.error', fallback = '')
	if testing_error == 'env_session_error':
		env.session.start()
	with builddir.create(env, 'sadm.testing') as fh:
		fh.write('testing\n')
