# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm.listen.errors import error

__all__ = ['BitbucketProvider']

class BitbucketProvider(object):

	def auth(self, slug, req, cfg, data):
		for arg in ('name', 'uuid'):
			self._authRepo(arg, slug, cfg, data)

	def _authRepo(self, opt, slug, cfg, data):
		val = cfg.get("auth.%s" % opt, fallback = '')
		if val != '':
			try:
				x = data['repository'][opt]
				if x != val:
					raise error(403, "%s forbidden: %s %s" % (slug, opt, x))
			except KeyError:
				raise error(403, "%s forbidden: no %s" % (slug, opt))

	def validate(self, slug, cfg, data):
		for arg in ('nickname', 'uuid'):
			self._validUser(arg, slug, cfg, data)

	def _ls(self, val):
		r = []
		for l in val.splitlines():
			for x in l.split():
				r.append(x)
		return r

	def _validUser(self, opt, slug, cfg, data):
		val = cfg.get("auth.user.%s" % opt, fallback = '')
		if val != '':
			try:
				x = data['actor'][opt]
				if not x in self._ls(val):
					raise error(304, "%s no action: user %s %s" % (slug, opt, x))
			except KeyError:
				raise error(403, "%s forbidden: no user %s" % (slug, opt))

	def repoArgs(self, slug, cfg, action, data):
		args = {
			'repo.path': cfg.get('path'),
			'repo.branch': cfg.get('branch', fallback = 'master'),
		}
		try:
			actionData = data[action]['changes'][0]['new']
			chtype = actionData['type']
			branch = actionData['name']
			target = actionData['target']
			ttype = target['type']
			thash = target['hash'].strip()
		except KeyError as err:
			raise error(403, "%s forbidden: args %s" % (slug, err))
		if chtype != 'branch':
			raise error(304, "%s no action: change type %s" % (slug, chtype))
		if branch != args['repo.branch']:
			raise error(304, "%s no action: branch %s" % (slug, branch))
		if ttype != 'commit':
			raise error(304, "%s no action: target type %s" % (slug, ttype))
		if thash == '':
			raise error(403, "%s forbidden: target hash is empty" % slug)
		args['repo.checkout'] = thash
		return args
