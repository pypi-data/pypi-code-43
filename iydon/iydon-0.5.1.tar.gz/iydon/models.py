#!/usr/bin/env python
# coding: utf-8
'''Auxiliary models de Iydon.
'''
__all__ = ('ParseRecord', )
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
