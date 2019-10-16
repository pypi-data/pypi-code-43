#!/usr/bin/env python -m
# coding: utf-8
'''Main file de Iydon.
'''
if __name__ == '__main__':
	assert __package__, 'Please use `-m` option.'

	from IPython import embed

	import iydon
	from .config import embed_colors

	embed(colors=embed_colors)
