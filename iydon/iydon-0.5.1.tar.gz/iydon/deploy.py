#!/usr/bin/env python
# coding: utf-8
'''Deployment de Iydon.
'''
__all__ = ('Python_packages', 'Overleaf', 'LaTeX', 'R')
def __dir__() -> list: return __all__


import pip
if hasattr(pip, 'main'):
	from pip import main as pip_
else:
	from pip._internal import main as pip_

from . import config
from .config import py_pkgs_src, py_pkgs
from .config import overleaf_git, overleaf_man
from .config import latex_git
from .config import r_git

from .sites import get_link_by_subdomain
from .utils import typeassert, doc_format, yes_or_no


config.overleaf_man = overleaf_man = \
	get_link_by_subdomain('mma', full=True) + overleaf_man


@doc_format(set(py_pkgs.keys()))
@typeassert(bool, bool, bool, str)
def Python_packages(ask=True, all_=False, user=False, source='', **kwargs) -> bool:
	'''Install Python packages.

	Argument
	=======
		ask: bool, whether to use `yes_or_no`
		all_: bool, whether to install all packages
		user: bool, whether to use `--user`
		source: str, which PyPi website to use
		kwargs: in {}
	'''
	options = ['-i', source or py_pkgs_src]
	if user: options+=['--user']
	def install(pkgs:list):
		return pip_(['install'] + pkgs + options)

	_locals = dict()
	result = 0

	for pkg in py_pkgs:
		_locals[pkg] = kwargs.get(pkg, None)
		if _locals[pkg] is not None:
			continue

		if ask:
			msg = pkg.replace('_', ' ').capitalize()
			_locals[pkg] = yes_or_no(msg=msg, empty=False)
		elif all_:
			_locals[pkg] = True

	for pkg in py_pkgs:
		if _locals[pkg]:
			result += install(py_pkgs[pkg])

	return result==0


@typeassert()
def Overleaf() -> dict:
	'''Manual for deploying Overleaf.
	'''
	return {
		'github': overleaf_git,
		'manual': config.overleaf_man
	}


@typeassert()
def LaTeX() -> dict:
	'''Manual for deploying TeX live.
	'''
	return {
		'github': latex_git
	}


@typeassert()
def R() -> dict:
	'''Manual for deploying R.
	'''
	return {
		'github': r_git
	}
