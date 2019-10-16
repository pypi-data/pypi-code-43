#######################################################################################
#
#	Copyright (c) 2018, Wiphoo (Terng) Methachawalit, All rights reserved.
#
#######################################################################################


#######################################################################################
#
#	STANDARD IMPORTS
#

import numpy

#######################################################################################
#
#	LOCAL IMPORTS
#


#######################################################################################
#
#	GLOBAL VARIABLES
#


#######################################################################################
#
#	HELPER FUNCTIONS
#


#######################################################################################
#
#	CLASS DEFINITIONS
#

class ActivationFuncs:
	''' this class is designed storing an actication fucntion 
			and activation function derivative
	'''
	
	@staticmethod
	def activationFunc( x ):
		return ActivationFuncs.sigmoidFunc( x )
		
	@staticmethod
	def activationFuncDerivative( val ):
		return ActivationFuncs.sigmoidFuncDerivative( val )
	
	#	sigmoid functions
	@staticmethod
	def sigmoidFunc( x ):
		return 1.0 / ( 1.0 + numpy.exp( -x ) )
	
	@staticmethod
	def sigmoidFuncDerivative( val ):
		return val * ( 1.0 - val )
		
	
