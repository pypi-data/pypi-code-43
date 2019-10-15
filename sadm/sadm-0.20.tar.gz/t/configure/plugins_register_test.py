# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from glob import glob
from os import path

from _sadm import configure

_expectPlugins = dict(enumerate((
	'testing',
	'sadm',
	'sadmenv',
	'os',
	'os.pkg',
	'os.user',
	'sync',
	'network.iptables',
	'vcs.clone',
	'docker',
	'service',
	'service.postfix',
	'service.docker',
	'service.munin',
	'service.munin_node',
	'service.apache',
	'network.fail2ban',
)))

def test_plugins_list():
	idx = 0
	for p in configure.pluginsList():
		assert (idx, p) == (idx, _expectPlugins[idx])
		idx += 1

def test_plugins_list_revert():
	idx = max(_expectPlugins.keys())
	for p in configure.pluginsList(revert = True):
		assert (idx, p) == (idx, _expectPlugins[idx])
		idx -= 1

def test_plugins_new():
	known = {}
	for n in _expectPlugins.values():
		known[n] = True
	for p in configure.pluginsList():
		assert known.get(p, False), "new unknown plugin: %s" % p

def test_plugins_list_match_fs():
	pl = list(configure.pluginsList())
	fs = glob(path.join('_sadm', 'plugin', '*', 'config.ini'))
	fs.extend(glob(path.join('_sadm', 'plugin', '**', 'config.ini')))
	fs.extend(glob(path.join('_sadm', 'plugin', '**', '*', 'config.ini')))
	fsok = {}
	for x in fs:
		fsok['.'.join(x.split(path.sep)[2:-1])] = True
	fs = [x for x in fsok.keys()]
	fs.remove('skel')
	fs.append('testing')
	fs = sorted(fs)
	pl = sorted(pl)
	print('-- PL:', pl)
	print('-- FS:', fs)
	assert fs == pl
	assert fs == sorted([n for _, n in _expectPlugins.items()])
