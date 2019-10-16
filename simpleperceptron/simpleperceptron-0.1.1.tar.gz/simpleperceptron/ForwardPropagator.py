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

#	activation function
from ActivationFuncs import ActivationFuncs

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

class ForwardPropagator:
	''' this class is designed for storing the inputs matrix
			inputs matrix for a hidden layer neurons and inputs matrix for a output layer
	'''
	
	def __init__( self, inputsMatrix ):
		
		#	inputs matrix
		self.inputsMatrix = inputsMatrix
		
		#	outputs matrix for a hidden layer neurons
		self.outputsMatrixHiddenLayerNeurons = None
		
		#	outputs for a output layer
		self.outputsMatrixOutputsLayer = None
		
	def propagate( self, perceptron ):
		''' do a forward propagate changes from inputs matrix through 
				outputs matrix for a hidden layer neurons then through
				outputs matrix for outputs layer
		'''
		
#		print( 'ForwardPropagator.propagate()...............' )
#		print( '                   self.inputsMatrix = {}'.format( self.inputsMatrix ) )
#		print( '                   type( self.inputsMatrix ) = {}'.format( type( self.inputsMatrix ) ) )
#		print( '                   self.inputsMatrix.shape = {}'.format( self.inputsMatrix.shape ) )
#
#		print( '                   perceptron.hiddenLayerWeightsMatrix = {}'.format( perceptron.hiddenLayerWeightsMatrix ) )
#		print( '                   perceptron.hiddenLayerWeightsMatrix.shape = {}'.format( perceptron.hiddenLayerWeightsMatrix.shape ) )
#		print( '                   perceptron.outputLayerWeightsMatrix = {}'.format( perceptron.outputLayerWeightsMatrix ) )
#		print( '                   perceptron.outputLayerWeightsMatrix.shape = {}'.format( perceptron.outputLayerWeightsMatrix.shape ) )
		
		#	propagate inputs matrix and weight and bias on hidden layer neurons and
		#		this will be came ouputs matrix on hidden layer neurons
		self.outputsMatrixHiddenLayerNeurons = ActivationFuncs.activationFunc( numpy.dot( self.inputsMatrix,
																							perceptron.hiddenLayerWeightsMatrix ) \
#																				+ perceptron.hiddenLayerBiasMatrix )
)
		
		#	propagate outputs matrix on hidden layer neurons and weight and bias on output layer and
		#		this will be came ouputs matrix on outputs layer
		self.outputsMatrixOutputsLayer = ActivationFuncs.activationFunc( numpy.dot( self.outputsMatrixHiddenLayerNeurons,
																						perceptron.outputLayerWeightsMatrix ) \
#																			+ perceptron.outputLayerBiasMatrix )
)
		
		
#		print( '                   self.outputsMatrixHiddenLayerNeurons = {}'.format( self.outputsMatrixHiddenLayerNeurons ) )
#		print( '                   self.outputsMatrixOutputsLayer = {}'.format( self.outputsMatrixOutputsLayer ) )
#		print( 'DONE :: ForwardPropagator.propagate()...............' )
		
		
		

