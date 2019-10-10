# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

class TestingTask(object):
	def hook(self, action, args):
		if action == 'testing.error':
			raise RuntimeError('_exec task testing.error')
