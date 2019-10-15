# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json
from json import JSONDecodeError

from _sadm import log
from _sadm.errors import CommandError
from _sadm.listen import wapp
from _sadm.listen.exec import dispatch
from _sadm.listen.errors import error

from .provider.bitbucket import BitbucketProvider

__all__ = ['WebhookRepo']

_validVCS = {
	'git': True,
}
_provider = {
	'bitbucket': BitbucketProvider(),
}

#
# listen.cfg example
#
#   [webhook.repo:repotag]
#   provider = bitbucket
#   vcs = git
#   path = /usr/src/repotag
#   branch = master
#   auth.name = reponame
#   auth.uuid = 12345678
#   auth.user.name = user_nickname
#   auth.user.uuid = 12345678
#

class WebhookRepo(object):
	_cfg = None
	_prov = None
	_repoVCS = None
	_slug = None

	def __init__(self, provider, name):
		self._slug = "%s/%s" % (provider, name)
		prov = _provider.get(provider, None)
		if prov is None:
			raise error(400, "webhook invalid provider: %s" % provider)
		sect = "webhook.repo:%s" % name
		if not wapp.config.has_section(sect):
			sect = "sadm.webhook:%s" % name
			if not wapp.config.has_section(sect):
				raise error(400, "webhook %s repo not found: %s" % (provider, name))
		self._cfg = wapp.config[sect]
		self._prov = prov
		self._loadProvider(self._cfg, provider, name)
		self._loadRepo(self._cfg)

	def _loadProvider(self, cfg, provider, name):
		rProv = cfg.get('provider', fallback = 'none')
		if rProv != provider:
			raise error(400, "webhook %s: invalid provider: %s" % (self._slug, rProv))

	def _loadRepo(self, cfg):
		vcs = cfg.get('vcs', fallback = 'git')
		if not _validVCS.get(vcs, False):
			raise error(400, "webhook %s: invalid vcs: %s" % (self._slug, vcs))
		self._repoVCS = vcs

	def exec(self, req, action):
		log.debug("%s exec %s" % (self._slug, action))
		# TODO: check self._cfg.getboolean(action... if disabled raise error 400
		#       or just 200 with an "action disabled" message?
		# read body, it should be a valid json string
		try:
			obj = json.loads(req.body.read())
		except JSONDecodeError as err:
			raise error(400, "webhook %s: %s" % (self._slug, err))
		# authorize request info and json data
		self._prov.auth(self._slug, req, self._cfg, obj)
		# validate request data
		self._prov.validate(self._slug, self._cfg, obj)
		# get repo info from request data
		args = self._prov.repoArgs(self._slug, self._cfg, action, obj)
		# dispatch task
		task = "webhook.repo.%s" % self._repoVCS
		try:
			dispatch(req, task, action, args)
		except CommandError as err:
			raise error(500, "webhook %s: %s" % (self._slug, err))
