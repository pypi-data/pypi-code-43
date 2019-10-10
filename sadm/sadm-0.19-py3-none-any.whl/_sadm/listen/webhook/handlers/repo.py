# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import request

from _sadm.listen.webhook.repo import WebhookRepo

__all__ = ['repo']

def handle(provider, name, action):
	repo = WebhookRepo(provider, name)
	repo.exec(request, action)
	return 'OK\n'
