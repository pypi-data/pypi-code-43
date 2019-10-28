#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

def add_dynamo( *args, **kwargs ):
	'''
	Based upon:

	https://stackoverflow.com/questions/533382/dynamic-runtime-method-creation-code-generation-in-python
	https://stackoverflow.com/a/534597
	https://stackoverflow.com/a/533583
	'''

	skel		=	kwargs.pop( 'skel' )
	prefix		=	kwargs.pop( 'prefix' )
	number		=	kwargs.pop( 'number', None )
	cls			=	kwargs.pop( 'cls', None )
	docString	=	kwargs.pop( 'docs', None )

	def innerdynamo( self=None ):
		return skel( prefix, number, *args, **kwargs )
		pass # END FUNCTION

	innerdynamo.__name__	=	f"{ prefix }{ number }"
	innerdynamo.__doc__		=	docString if docString else f"docstring for { innerdynamo.__name__ }"

	# Method
	if cls:
		setattr(
			cls,
			innerdynamo.__name__,
			innerdynamo
		)

	# Function
	else:
		return innerdynamo

	pass # END FUNCTION : Add Dynamo
