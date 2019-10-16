#!/usr/bin/env python
__all__ = ('MacroParser', 'parse_macro', 'parse_macro_in')
def __dir__(): return __all__


from .models import MacroParser
from .utils import read_file


def parse_macro(content, cache=False):
	'''Parse macros.

	Argument
	=======
		content: str
		cache: bool, whether to cache the MacroParser
	'''
	_globals = globals()
	name = 'cached+macro+parser'
	if cache:
		if name in _globals:
			mp = _globals[name]
			# maybe let `mp.reload_content` return `self`
			mp.reload_content(content)
		else:
			_globals[name] = mp = MacroParser(content)
	else:
		mp = MacroParser(content)

	return mp.parse()

def parse_macro_in(file_name, cache=False):
	'''Parse macros in `file_name`.

	Argument
	=======
		content: str
		cache: bool, whether to cache the MacroParser
	'''
	return parse_macro(read_file(file_name), cache=cache)
