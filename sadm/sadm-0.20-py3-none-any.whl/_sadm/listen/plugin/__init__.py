# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import response

from _sadm import log

__all__ = ['ResponsePlugin']

class ResponsePlugin(object):
	api = 2
	name = 'sadm.listen.response'

	def setup(self, wapp):
		log.debug('setup')

	def apply(self, callback, ctx):
		log.debug("apply for rule: %s" % ctx.rule)
		def wrapper(*args, **kwargs):
			log.debug('apply.wrapper')
			resp = callback(*args, **kwargs)
			response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
			return resp
		return wrapper
