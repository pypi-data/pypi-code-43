#!/usr/bin/env python
from .config import flag_comment, flag_macro, flag_line, brackets
from .utils import record_print_in_function, read_file


class Stack:
	'''Stack.
	'''
	def __init__(self, *remains, reverse=False):
		self._stack = [*remains]
		if reverse: self._stack.reverse()

	def __bool__(self):
		return bool(self._stack)

	def push(self, element):
		self._stack.append(element)

	def pop(self):
		return self._stack.pop()


class MacroParser:
	r'''Macro parser.

	Macro Format
	=======
		\func_name(args)
	'''
	def __init__(self, content):
		self._content = content
		self._iter = iter(content)
		self._index = 0
		self._macros = dict()

	def __iter__(self):
		for char in self._iter:
			self._index += 1
			yield char


	# ======= public =======
	def builtins(self):
		'''Built-in macros.
		'''
		self._extract_until(brackets[0][1])
		is_builtin = lambda s: not s.startswith('_')
		return str(tuple(filter(is_builtin, dir(self))))

	def parse(self):
		result = ''
		for char in self:
			if char == flag_comment:
				self._extract_until(flag_line)
			elif char == flag_macro:
				result += self._parse_macro()
			else:
				result += char
		return result

	def renew_macro(self):
		'''Re-define the macro.
		'''
		return self.new_macro(renew=True)

	def new_macro(self, renew=False):
		'''Define a new macro.

		Argument
		=======
			renew: bool, if renew, then macro not in self._macros
		'''
		body = self._extract_group(brackets[0], start=brackets[0][0])
		parser = MacroParser(body)
		for char in parser:
			if char == flag_macro:
				name = parser._extract_until(brackets[0][0])
				args = parser._extract_group(brackets[0], start=brackets[0][0])
				parser._extract_until(brackets[2][0])
				defn = parser._extract_group(brackets[2], start=brackets[2][0])
				exec(f'def {name}({args}):{defn}')
				if __debug__:
					if renew:
						msg = f'Cannot re-define `{name}`.'
						assert name in self._macros, msg
					else:
						msg = f'Already define `{name}`.'
						assert name not in self._macros, msg
				self._macros[name] = locals()[name]
		return ''

	def verb(self):
		'''Verb environment.
		'''
		return self._extract_until(brackets[0][1])

	def verb_(self):
		'''Verb environment with paired delimiters.
		'''
		return self._extract_group(brackets[0], start=brackets[0][0])

	def input(self):
		'''Input file.
		'''
		file = self._extract_group(brackets[0], start=brackets[0][0])
		parser = MacroParser(read_file(file))
		return parser.parse()


	# ======= private =======
	def _parse_macro(self):
		name = self._extract_until(brackets[0][0])
		if hasattr(self, name):
			return getattr(self, name)()
		elif name in self._macros:
			args = self._extract_group(brackets[0], start=brackets[0][0])
			def func():
				_macros = self._macros
				_name = name
				_args = args
				exec(f'_macros["{_name}"]({_args})')
			return record_print_in_function(func)
		elif __debug__:
			msg = f'Undefined macro `{name}`.'
			raise Exception(msg)
		return ''

	def _extract_until(self, *delimiters, include=False):
		'''Extract text until meet `delimiters`.

		Argument
		=======
			delimiters: tuple[str]
			include: bool, whether to include the end delimiter
		'''
		start = self._index
		for char in self:
			if char in delimiters:
				break
		else:
			if __debug__:
				msg = f'No delimiters found in {delimiters}.'
				raise Exception(msg)
		index = slice(start, self._index-1+include)
		return self._content[index]

	def _extract_group(self, *groups, start=None, include=False):
		'''Extract group by `groups`.

		Argument
		=======
			groups: tuple[tuple], for element in groups, len(element)=2
			include: bool, whether to include the end delimiter
		'''
		stack = Stack(start) if start else Stack()
		start = self._index
		for char in self:
			for group in groups:
				if char == group[0]:
					stack.push(group[0])
					break
				elif char == group[1]:
					temp = stack.pop()
					if __debug__:
						msg = f'Unpaired group in {group}'
						assert temp==group[0], msg
					break
			if not stack:
				index = slice(start, self._index-1+include)
				return self._content[index]
		else:
			if __debug__:
				msg = f'Unbounded groups in {groups}.'
				raise Exception(msg)
