# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from bottle import response, HTTPError, request, HTTP_CODES

from _sadm import log

__all__ = ['init', 'error']

def _handler(code, error):
	log.debug("handler %d" % code)
	log.debug("%d - %s" % (error.status_code, error.status_line))
	argsLen = len(error.args)
	if argsLen >= 3:
		log.error("%s %d - %s" % (request.remote_addr, code, error.args[2]))
		if argsLen >= 4:
			log.debug("%s" % error.args[3])
	else:
		log.error("%s %d - %s" % (request.remote_addr, code, request.path))
	response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
	if code == 304:
		# 304 response should not include body content
		return ''
	codeStatus = HTTP_CODES.get(code, None)
	if codeStatus is not None:
		return "%s\n" % codeStatus
	return "ERROR %d\n" % code

_initDone = False

def init(wapp):
	global _initDone

	@wapp.error(304)
	def error_304(error):
		return _handler(304, error)

	@wapp.error(400)
	def error_400(error):
		return _handler(400, error)

	@wapp.error(403)
	def error_403(error):
		return _handler(403, error)

	@wapp.error(404)
	def error_404(error):
		return _handler(404, error)

	@wapp.error(405)
	def error_405(error):
		return _handler(405, error)

	@wapp.error(500)
	def error_500(error):
		return _handler(500, error)

	_initDone = True

def error(code, msg):
	log.error("%s %d - %s" % (request.remote_addr, code, msg))
	return HTTPError(
		status = code,
		body = msg,
	)
