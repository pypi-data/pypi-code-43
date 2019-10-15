# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json
from bottle import request

from _sadm import log
from _sadm.listen.errors import error
from _sadm.listen.webhook.repo.vcs.git import GitRepo

__all__ = ['exech']

_taskman = {
	'webhook.repo.git': GitRepo(),
}

def handle(task, action):
	log.debug("exec handle: %s %s" % (task, action))
	taskman = _taskman.get(task, None)
	if taskman is None:
		raise error(500, "listen.exec task %s: no manager" % task)
	try:
		args = json.load(request.body)
		taskman.hook(action, args)
	except Exception as err:
		raise error(500, "%s" % err)
	return 'OK\n'
