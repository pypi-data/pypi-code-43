# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

from os.path import realpath, dirname, join, normpath, sep

__all__ = ['fpath', 'fopen']

_srcdir = realpath(dirname(__file__))

def root():
	return _srcdir

def fpath(*parts):
	n = join(*parts)
	n = normpath(n)
	while n.startswith(sep):
		n = n.replace(sep, '', 1)
	return join(_srcdir, n)

def fopen(*parts):
	return open(fpath(*parts), 'r', encoding = 'utf-8')
