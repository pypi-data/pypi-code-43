#!/usr/bin/env python
# coding: utf-8
'''Auxiliary file de Iydon.
'''
__all__ = ('typeassert', 'domain_join', 'yes_or_no', 'json_loads_online',
	'ping_link', 'lazy_property')
def __dir__() -> list: return __all__


from inspect import signature
from functools import wraps
from json import loads
from requests import get, head
from typing import Iterable, Callable


def typeassert(*t_args, **t_kwargs):
	'''Enforce type check on function using decorator.

	Todo
	=======
	Check the type of return value.

	References
	=======
	(Python Cookbook)[https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p07_enforcing_type_check_on_function_using_decorator.html]
	'''
	def decorate(func):
		# If in optimized mode, disable type checking
		if not __debug__:
			return func

		# Map function argument names to supplied types
		σ = signature(func)
		bound_types = σ.bind_partial(*t_args, **t_kwargs).arguments

		@wraps(func)
		def wrapper(*args, **kwargs):
			bound_values = σ.bind(*args, **kwargs)
			# Enforce type assertions across supplied arguments
			for name, value in bound_values.arguments.items():
				if name in bound_types:
					if not isinstance(value, bound_types[name]):
						raise TypeError(
							'Argument `{}` must be {}.'.format(name, bound_types[name])
						)
			return func(*args, **kwargs)
		return wrapper
	return decorate


@typeassert()
def doc_format(*args, **kwargs):
	'''__doc__.format
	'''
	def decorate(func):
		func.__doc__ = func.__doc__.format(*args, **kwargs)
		return func
	return decorate


@typeassert(Iterable, bool, bool)
def domain_join(domains, full=False, https=False):
	'''Join domain and subdomain.

	Argument
	=======
		domains: Iterable[str]
		full: bool, whether to return full link
		https: bool, whether to use HTTP Secure
	'''
	# If in optimized mode, disable type checking
	if __debug__:
		for value in domains:
			assert isinstance(value, str), 'Argument must be Iterable with all str.'

	if full:
		return ('https://' if https else 'http://') + '.'.join(domains)
	else:
		return '.'.join(domains)


@typeassert(str, bool)
def yes_or_no(msg='', empty=True):
	'''Yes or No.

	Argument
	=======
		msg: str, prompt message
		empth: bool, if input is empty, then return `empty`
	'''
	prompt = ' [y/N, empty is {}]: '.format('y' if empty else 'N')
	while True:
		option = input(msg + prompt)
		if option:
			if 'y' in option.lower():
				return True
			elif 'n' in option.lower():
				return False
		else:
			return empty


@typeassert(str)
def json_loads_online(url):
	'''Deserialize json data from `url`.

	Todo
	=======
	[GitHub API](https://api.github.com/)

	Argument
	=======
		url: str
	'''
	response = get(url)
	return loads(response.text)


@typeassert(str, (int, float))
def ping_link(link, timeout=3, **kwargs):
	'''Ping link from `link`.

	Argument
	=======
		link: str
		timeout: int or float, timeout seconds
		kwargs: keywords argument of `requests.request`
	'''
	try:
		response = head(link,  timeout=timeout, **kwargs)
		return response.status_code < 400 \
			or response.status_code in (999, )
	except Exception as e:
		print(e)
		return False


@typeassert(Callable)
def lazy_property(func):
	'''Lazy property.

	References
	=======
	(Python Cookbook)[https://python3-cookbook.readthedocs.io/zh_CN/latest/c08/p10_using_lazily_computed_properties.html]

	Example
	=======
		>>> import math
		>>> class Circle:
		... 	def __init__(self, radius):
		... 		self.radius = radius
		... 	@lazy_property
		... 	def area(self):
		... 		print('Computing area')
		... 		return math.pi * self.radius**2
	'''
	name = '_lazy_' + func.__name__
	@property
	def lazy(self):
		if hasattr(self, name):
			return getattr(self, name)
		else:
			value = func(self)
			setattr(self, name, value)
			return value
	return lazy
