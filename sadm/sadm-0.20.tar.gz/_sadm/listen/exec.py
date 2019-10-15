# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import json
import sys
from urllib.parse import urlparse

from _sadm import log, libdir, version
from _sadm.listen.client import ListenClient
from _sadm.utils import sh, path
from _sadm.utils.cmd import callCheck

__all__ = ['dispatch', 'main']

#
# webhook dispatch task (exec new process)
#

def dispatch(req, task, action, taskArgs):
	log.debug("dispatch task: %s - action: %s" % (task, action))
	reqURL = _getURL(req)
	obj = {
		'sadm.log': log.curLevel(),
		'sadm.listen.url': reqURL,
		'task': task,
		'task.action': action,
		'task.args': taskArgs,
	}
	taskfn = None
	with sh.mktmp(prefix = __name__, suffix = ".%s.json" % task) as fh:
		taskfn = fh.name()
		fh.write(json.dumps(obj))
	_sched(taskfn)

def _getURL(req):
	# ~ for k, v in req.headers.items():
		# ~ log.debug("%s: %s" % (k, v))
	u = urlparse(req.url)
	scheme = u.scheme
	if not scheme: # pragma: no cover
		scheme = 'http'
	port = u.port
	if not port:
		port = '3666'
	url = "%s://127.0.0.1:%s" % (scheme, port)
	log.debug("URL: %s" % url)
	return url

_pycmd = path.join(sys.exec_prefix, 'bin', 'python3')
_selfpath = libdir.fpath('listen', 'exec.py')

def _sched(taskfn):
	log.debug("exec prefix %s" % sys.exec_prefix)
	cmd = [_pycmd, _selfpath, taskfn]
	atcmd = "echo '%s' | at now" % ' '.join(cmd)
	log.debug("run: %s" % atcmd)
	callCheck(atcmd)

#
# task exec main (runs under a new process)
#

def main(args):
	if len(args) != 1:
		print('ERROR: sadm-listen exec invalid args', file = sys.stderr)
		return 1
	taskfn = args[0]
	obj = None
	try:
		with open(taskfn, 'r') as fh:
			obj = json.load(fh)
	except Exception as err:
		log.error("%s" % err)
		return 2
	finally:
		path.unlink(taskfn)
	log.init(obj.get('sadm.log', 'warn'))
	log.debug(version.string('sadm-listen'))
	log.debug("task file %s" % taskfn)
	task = obj.get('task', None)
	if task is None:
		log.error('listen.exec task not set')
		return 3
	taskAction = obj.get('task.action', None)
	if taskAction is None:
		log.error("listen.exec task %s: no action" % task)
		return 4
	taskArgs = obj.get('task.args', None)
	if taskArgs is None:
		log.error("listen.exec task %s: no args" % task)
		return 5
	cliURL = obj.get('sadm.listen.url', 'http://127.0.0.1:3666')
	cli = ListenClient(cliURL)
	return cli.exec(task, taskAction, taskArgs)

if __name__ == '__main__': # pragma: no cover
	sys.exit(main(sys.argv[1:]))
