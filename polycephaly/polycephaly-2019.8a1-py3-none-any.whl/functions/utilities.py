#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

def invertedDict( d ):
	'''
	Sourced from https://stackoverflow.com/questions/483666/python-reverse-inverse-a-mapping
	'''
	return { v: k for k, v in d.items() }
	pass

def getType( v ):
	'''
	'''

	return type( v ).__name__
	pass # END FUNCTION: getType()

def easySwitch( match, default=None, **kwargs ):
	'''
	'''

	for k, v in kwargs.items():

		if k == match:
			return v
			pass # END IF

		pass # END FOR

	return default

	pass # END FUNCTION : Easy Switch

class switch(object):
	'''
	This class provides the functionality we want. You only need to look at
	this if you want to know how this works. It only needs to be defined
	once, no need to muck around with its internals.
	http://code.activestate.com/recipes/410692/
	'''

	def __init__(self, value):
		self.value = value
		self.fall = False

	def __iter__(self):
		"""Return the match method once, then stop"""
		yield self.match
		raise StopIteration
    
	def match(self, *args):
		"""Indicate whether or not to enter a case suite"""
		if self.fall or not args:
			return True
		elif self.value in args: # changed for v1.5, see below
			self.fall = True
			return True
		else:
			return False

	pass # END CLASS: SWITCH()
