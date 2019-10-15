# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from urllib import request

__all__ = ['urlopen']

class _Net(object):
	def __init__(self):
		self.urlopen = request.urlopen

_net = _Net()

def urlopen(url, data = None, timeout = None, context = None):
	return _net.urlopen(url, data = data, timeout = timeout, context = context)
