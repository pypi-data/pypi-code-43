# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import HTTPError
from pytest import raises

from _sadm.listen.webhook import repo

PROVIDERS = [
	'bitbucket',
	'testing',
]

def test_providers_list():
	assert sorted(repo._provider.keys()) == PROVIDERS

def test_noprovider():
	with raises(HTTPError) as exc:
		repo.WebhookRepo('noprov', 'testing')
	err = exc.value
	assert err.status_code == 400
	assert err.body == 'webhook invalid provider: noprov'

def test_norepo(listen_wapp):
	with listen_wapp():
		with raises(HTTPError) as exc:
			repo.WebhookRepo('testing', 'norepo')
		err = exc.value
		assert err.status_code == 400
		assert err.body == 'webhook testing repo not found: norepo'

def test_json_error(listen_wapp):
	with listen_wapp(profile = 'testing') as wapp:
		r = repo.WebhookRepo('testing', 'testing')
		with raises(HTTPError) as err:
			r.exec(wapp.request(), 'testing')
		wapp.checkException(err, 400, 'testing/testing: Expecting value')
