# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.configure import pluginsList

def test_configure_testing(testing_plugin):
	p = testing_plugin('testing', ns = '_sadmtest')
	assert p.configure()

def test_all_configure(testing_plugin):
	for n in pluginsList():
		if n == 'testing':
			continue
		print('-- configure plugin:', n)
		p = testing_plugin(n)
		assert p.configure(), "%s plugin.configure failed" % n
