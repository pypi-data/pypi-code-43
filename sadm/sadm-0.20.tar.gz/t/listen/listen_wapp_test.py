# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import bottle
import json

from collections import namedtuple
from configparser import ConfigParser
from glob import glob
from os import path
from pytest import raises

from _sadmtest import mock

from _sadm.listen import wapp, errors

def test_default_config():
	assert wapp.config is None

def test_config_error():
	cfgfn = path.join('tdata', 'no-listen.cfg')
	with raises(FileNotFoundError):
		w = wapp.init(cfgfn = cfgfn)

ROUTES = [
	'_exec /_/exec/<task>/<action> POST',
]

def test_default_wapp(listen_wapp):
	assert not errors._initDone
	with listen_wapp() as w:
		assert errors._initDone
		assert sorted([p.name for p in w.plugins]) == ['sadm.listen.response']
		routes = []
		for r in w.routes:
			routes.append(' '.join([str(r.name), r.rule, r.method]))
		assert sorted(routes) == ROUTES

def test_wapp(listen_wapp):
	with listen_wapp() as w:
		assert w.name == 'listen'
		assert w.response is None

WEBHOOK_ROUTES = ROUTES[:]
WEBHOOK_ROUTES.extend([
	'hook.repo /hook/<provider>/<name>/<action> POST',
])

def test_webhook_routes(listen_wapp):
	with listen_wapp(profile = 'testing') as w:
		assert w.name == 'listen'
		assert w.response is None
		routes = []
		for r in w.routes:
			routes.append(' '.join([str(r.name), r.rule, r.method]))
		assert sorted(routes) == WEBHOOK_ROUTES

Handler = namedtuple('Handler', ['name', 'args', 'method'])
def newHandler(dat):
	return Handler(
		name = dat['handler']['name'],
		args = dat['handler'].get('args', []),
		method = dat['handler'].get('method', 'POST'),
	)

Response = namedtuple('Response', ['status', 'error', 'content'])
def newResponse(dat):
	err = dat.get('response.error', None)
	if err is None:
		return Response(
			status = 200,
			error = False,
			content = dat.get('response', 'OK'),
		)
	else:
		return Response(
			status = err.get('status', 400),
			error = True,
			content = err.get('match', None),
		)

def test_all(listen_wapp):
	patterns = [
		path.join('tdata', 'listen', '*', 'listen.cfg'),
		path.join('tdata', 'listen', '*', '*', 'listen.cfg'),
	]
	cfgfiles = {}
	for patt in patterns:
		for fn in glob(patt):
			cfgfiles[fn] = True
	with mock.log():
		with mock.utils(None):
			for fn in sorted(cfgfiles.keys()):
				profile = fn.replace(path.join('tdata', 'listen'), '', 1)
				profile = '/'.join(profile.split(path.sep)[:-1])
				if profile.startswith('/'):
					profile = profile[1:]
					_testProfile(listen_wapp, profile, fn)

def _mockConfig(fn):
	return wapp._newConfig(fn)

def _testProfile(listen_wapp, profile, cfgfn):
	print(profile, cfgfn)
	profdir = path.dirname(cfgfn)
	for datfn in sorted(glob(path.join(profdir, '*.json'))):
		datname = path.basename(datfn).replace('.json', '').strip()
		print(' ', datname, datfn)
		with open(datfn, 'r') as fh:
			dat = json.load(fh)
		h = newHandler(dat)
		resp = newResponse(dat)
		with mock.utils(_mockConfig(cfgfn), tag = datname):
			with listen_wapp(profile = profile) as wapp:
				hfunc = _getHandler(wapp, h.name)
				if resp.error:
					with raises(bottle.HTTPError) as exc:
						if h.method == 'POST':
							_wappPOST(wapp, datname, hfunc, h.args)
					wapp.checkException(exc, resp.status, resp.content)
				else:
					if h.method == 'POST':
						_wappPOST(wapp, datname, hfunc, h.args)
					assert wapp.response == resp.content

def _getHandler(wapp, name):
	for r in wapp.routes:
		if r.name == name:
			return r.callback
	assert False, "wapp handler not found: %s" % name

def _wappPOST(wapp, datname, hfunc, hargs):
	wapp.POST(datname, hfunc, *hargs)
