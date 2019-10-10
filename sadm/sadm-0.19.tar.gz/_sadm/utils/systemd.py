# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from _sadm import libdir
from _sadm.utils import builddir, path
from _sadm.utils.cmd import call, callCheck

__all__ = ['status', 'start', 'stop', 'restart', 'reload', 'enable', 'configure']

_ctlcmd = ['systemctl', '--quiet', '--no-pager', '--no-legend', '--no-ask-password']

def _cmd(service, action, *args, check = True):
	cmd = []
	cmd.extend(_ctlcmd)
	cmd.extend(args)
	cmd.append(action)
	cmd.append(service)
	if check:
		return callCheck(cmd)
	return call(' '.join(cmd))

def status(service, check = 'is-active'):
	return _cmd(service, check, check = False)

def start(service, *args):
	return _cmd(service, 'start', *args)

def stop(service, *args):
	return _cmd(service, 'stop', *args)

def restart(service, *args):
	return _cmd(service, 'restart', *args)

def reload(service, *args):
	return _cmd(service, 'reload', *args)

def enable(service, *args):
	return _cmd(service, 'enable', *args)

def configure(env, unit, typ, name, tpldat):
	service = "%s-%s.%s" % (unit, name, typ)
	with libdir.fopen('utils', 'systemd', "%s.%s" % (unit, typ)) as fh:
		data = fh.read()
	dst = path.join('etc', 'systemd', 'system', service)
	with builddir.create(env, dst) as fh:
		fh.write(data.format(**tpldat))
		fh.flush()
