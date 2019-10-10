# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os import path

from _sadm.configure import pluginsList
from _sadm.env.settings import Settings

_srcdir = path.dirname(path.dirname(path.dirname(__file__)))

def test_build_testing(testing_plugin):
	print('-- build plugin: testing')
	p = testing_plugin('testing', ns = '_sadmtest', cfgfn = 'build.ini')
	p.build()
	p.check.builddir.file('sadm.testing') # just to check it works both ways
	p.check.builddir.file('sadm.testing', 'testing\n')

# ~ def test_build_vcs_clone(testing_plugin):
	# ~ print('-- build plugin: vcs.clone')
	# ~ p = testing_plugin('vcs.clone', cfgfn = 'build.ini')
	# ~ p.build()

def test_all_build(testing_plugin):
	pl = list(pluginsList())
	print('-- plugins list:', pl)
	for n in pl:
		if n == 'testing':
			continue
		print('-- build plugin:', n)
		_pbuild(testing_plugin, n, 'build.ini')

def _pbuild(pnew, pname, cfgfn):
	fn = path.join(_srcdir, 'tdata', 'plugin',
		pname.replace('.', path.sep), 'config', cfgfn)
	if path.isfile(fn):
		p = pnew(pname, cfgfn = cfgfn)
		p.build()
		# check assets/testing.txt was sync'ed
		# so, all build tests should do that, yes...
		p.check.builddir.file('testing.txt', 'testing\n')
		_pcheck(p, fn)

def _pcheck(p, fn):
	pcfg = Settings()
	with open(fn, 'r') as fh:
		pcfg.read_file(fh)
	if pcfg.has_section('_sadmtest.check'):
		for opt, val in pcfg.items('_sadmtest.check'):
			if opt.startswith('builddir.file.'):
				_checkBuilddirFile(p, val)

def _checkBuilddirFile(p, args):
	fn = args.split()[0]
	if fn.startswith(path.sep):
		fn = fn.replace(path.sep, '', 1)
	try:
		cksum = args.split()[1]
	except IndexError:
		cksum = None
	p.check.builddir.file(fn, checksum = cksum)
