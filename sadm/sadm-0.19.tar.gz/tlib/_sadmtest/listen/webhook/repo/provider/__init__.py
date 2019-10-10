# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

__all__ = ['TestingProvider']

class TestingProvider(object):

	def auth(self, slug, req, cfg, data):
		pass

	def validate(self, slug, cfg, data):
		pass

	def repoArgs(self, slug, cfg, action, data):
		return {}
