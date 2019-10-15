#!/usr/bin/env python
__all__ = ('MacroParser', 'parse_macro', 'parse_macro_in')
def __dir__(): return __all__


from .models import MacroParser
from .utils import read_file


def parse_macro(content):
	return MacroParser(content).parse()

def parse_macro_in(file_name):
	return parse_macro(read_file(file_name))
