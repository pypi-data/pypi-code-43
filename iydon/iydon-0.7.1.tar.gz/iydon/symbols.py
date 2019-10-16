#!/usr/bin/env python
# coding: utf-8
'''Greek symbols
'''
names = ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
	'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma',
	'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega')
__all__ = names + ('as_dict', )
def __dir__() -> list: return __all__


from .utils import typeassert


symbols = ('α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι℩', 'κ', 'λ', 'μ', 'ν', 'ξ',
	'ο', 'π', 'ρ', 'ςσ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω')
# - Ι ι ℩ 有时用来表示微细的差别
# - Σ σ ς 在希腊语中，如果一个单词的最末一个字母是小写σ，要把该字母写成 ς

_locals = locals()
for _ in zip(names, symbols):
	_locals[_[0]] = _[1]

@typeassert()
def as_dict() -> dict:
	'''Return symbols as dict.
	'''
	return dict(zip(names, symbols))
