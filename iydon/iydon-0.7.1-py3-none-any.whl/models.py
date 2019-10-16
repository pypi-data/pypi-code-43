#!/usr/bin/env python
# coding: utf-8
'''Auxiliary models de Iydon.
'''
__all__ = ('ParseRecord', 'DemoCode', 'lazy_property')
def __dir__() -> list: return __all__


from collections import namedtuple


ParseRecord = namedtuple('ParseRecord', ('link', 'type', 'https'))


class DemoCode:
	'''Demo code with some notes.
	'''
	__slots__ = ('_code', '_note')

	def __init__(self, code, note):
		self._code = code
		self._note = note

	def __repr__(self):
		print(self._note)
		return self._code

	def __call__(self):
		return self.run(debug=True)

	@property
	def code(self): return self._code

	@property
	def note(self): return self._note

	def run(self, debug=False):
		'''Execute the demo code.

		Return
		=======
			None or Boolean (if debug)
		'''
		flag = True
		try:
			if isinstance(self.code, (tuple, list)):
				for code in self.code:
					exec(code)
			elif isinstance(self.code, str):
				exec(self.code)
		except Exception as e:
			print(e)
			flag = False

		if debug: return flag


class lazy_property:
	'''Lazy property

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
	def __init__(self, func):
		self.func = func

	def __get__(self, instance, cls):
		if instance is None:
			return self
		else:
			value = self.func(instance)
			setattr(instance, self.func.__name__, value)
			return value
