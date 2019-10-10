# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

import tarfile

from hashlib import md5
from os import stat

from _sadm.utils import path

__all__ = ['deploy']

# run as root at first pass
sumode = 'pre'

def deploy(env):
	fn = env.name() + '.tar'
	fpath = env.assets.rootdir(env.name(), fn)
	mtime = stat(fpath).st_mtime
	target = env.settings.get('sadmenv', 'target.dir')
	env.log("%s %s" % (fn, mtime))
	env.log("target %s" % target)
	with open(fpath, 'rb') as fh:
		tar = tarfile.open(fn, 'r:', fileobj = fh)
		try:
			for tinfo in tar:
				tinfo.mtime = mtime
				if _syncTarget(env, target, tar, tinfo):
					env.log("  %s" % tinfo.name)
					tar.extract(tinfo, path = target, set_attrs = True)
				else:
					env.debug("  %s OK" % tinfo.name)
		finally:
			tar.close()

def _syncTarget(env, target, tar, tinfo):
	dst = path.join(target, tinfo.name)
	env.debug("check target %s" % dst)
	if tinfo.isfile():
		return _checkFile(env, dst, tar, tinfo)
	return _checkAttrs(env, dst, tinfo)

def _checkAttrs(env, dst, tinfo):
	try:
		st = stat(dst)
	except FileNotFoundError:
		env.debug("  %s not found" % dst)
		return True
	stmode = oct(st.st_mode & 0o777)
	tmode = oct(tinfo.mode)
	if tinfo.isfile():
		if st.st_size != tinfo.size:
			env.debug("  %s size got %d expect %d" % (dst, st.st_size, tinfo.size))
			return True
	if stmode != tmode:
		env.debug("  %s mode got %s expect %s" % (dst, stmode, tmode))
		return True
	# TODO: check user/group
	return False

def _checkFile(env, dst, tar, tinfo):
	if _checkAttrs(env, dst, tinfo):
		return True
	else:
		h = md5()
		with open(dst, 'rb') as fh:
			h.update(fh.read())
		srcChecksum = h.hexdigest()
		del h
		h = md5()
		with tar.extractfile(tinfo.name) as fh:
			h.update(fh.read())
		dstChecksum = h.hexdigest()
		if dstChecksum != srcChecksum:
			env.debug("  %s checksum got %s expect %s" % (dst, dstChecksum, srcChecksum))
			return True
	return False
