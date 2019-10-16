#!/usr/bin/env python
import sys
import tempfile


def read_file(file_name, encoding='utf-8'):
	'''读取文件.

	Argument
	=======
		file_name: str
		encoding: str
	'''
	if encoding:
		with open(file_name, 'r', encoding=encoding) as f:
			return f.read()
	else:
		with open(file, 'rb') as f:
			return f.read()


def record_print_in_function(func, args=(), kwargs={}, encoding='utf-8'):
	'''记录函数中`print`函数的结果.

	Argument
	=======
		func(*args, **kwargs), Callable, return None
	'''
	with tempfile.TemporaryFile('w+t', encoding=encoding) as f:
		stdout = sys.stdout
		sys.stdout = f
		func(*args, **kwargs)
		sys.stdout = stdout
		f.seek(0)
		return f.read()
