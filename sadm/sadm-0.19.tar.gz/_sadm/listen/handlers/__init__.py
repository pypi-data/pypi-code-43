# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import log
from _sadm.listen.handlers import exec as _exec
from _sadm.listen.webhook.handlers import repo
from _sadm.listen.plugin import ResponsePlugin

__all__ = ['init']

def init(wapp, config):
	wapp.install(ResponsePlugin())

	wapp.route('/_/exec/<task>/<action>', 'POST', _exec.handle, name = '_exec')

	initDone = {}
	for sect in config.sections():
		if sect.startswith('sadm.webhook:') or sect.startswith('webhook.repo:'):
			if not initDone.get('webhook', False):
				log.debug('enable webhook')
				_initWebhooks(wapp)
				initDone['webhook'] = True

def _initWebhooks(wapp):
	wapp.route('/hook/<provider>/<name>/<action>', 'POST', repo.handle, name = 'hook.repo')
