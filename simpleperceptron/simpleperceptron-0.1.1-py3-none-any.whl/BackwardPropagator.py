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

class BackwardPropagator:
	''' this class is designed for storing delta weights at hidden layer and output layer
	''' 
	
	def __init__( self ):
		
		#	errors on each layer
		#		at hidden layer
		self.hiddenLayerErrorsMatrix = None
		#		at output layer
		self.outputErrorsMatrix = None
		
		#	delta errors on each layer
		#		at hidden layer
		self.hiddenLayerDeltaErrorsMatrix = None
		#		at output layer
		self.outputDeltaErrorsMatrix = None
		
		#	delta weights on each layer
		#		at hidden layer
		self.hiddenLayerDeltaWeightsMatrix = None
		#		at output layer
		self.outputDeltaWeightsMatrix = None
		
	def propagate( self, perceptron, forwardPropagator, targetOutputsMatrix, learningRate ):
		''' calculate the error deltas on each layers
		'''
		
#		print( 'BackwardPropagator.propagate()...............' )
#		print( '       targetOutputsMatrix = {}'.format( targetOutputsMatrix ) )
		
		####################################################################
		#	calculate errors and delta errors
		
		####################################################################
		#	output layer
		
		#	calculate errors at outputs layer
		self.outputErrorsMatrix = ( targetOutputsMatrix - forwardPropagator.outputsMatrixOutputsLayer )
		
#		print( '                 forwardPropagator.outputsMatrixOutputsLayer = {}'.format( forwardPropagator.outputsMatrixOutputsLayer ) )
#		print( '                 forwardPropagator.outputsMatrixOutputsLayer.shape = {}'.format( forwardPropagator.outputsMatrixOutputsLayer.shape ) )
#		print( '                 type( forwardPropagator.outputsMatrixOutputsLayer ) = {}'.format( type( forwardPropagator.outputsMatrixOutputsLayer ) ) )
				
		#	calculate delta errors at output layer
		self.outputDeltaErrorsMatrix = self.outputErrorsMatrix * ActivationFuncs.activationFuncDerivative( 
																			forwardPropagator.outputsMatrixOutputsLayer )
		
#		print( '           self.outputErrorsMatrix = {}'.format( self.outputErrorsMatrix ) )
#		print( '           self.outputDeltaErrorsMatrix = {}'.format( self.outputDeltaErrorsMatrix ) )		
		
		####################################################################
		#	hidden layer
		
		#	calculate errors at hidden layer neurons
		self.hiddenLayerErrorsMatrix = self.outputDeltaErrorsMatrix.dot( perceptron.outputLayerWeightsMatrix.T )
#												+ perceptron.outputLayerBiasMatrix
		
		#	calulate delta errors at hidden layer neurons
		self.hiddenLayerDeltaErrorsMatrix = self.hiddenLayerErrorsMatrix * ActivationFuncs.activationFuncDerivative(
																				forwardPropagator.outputsMatrixHiddenLayerNeurons )
		
#		print( '           self.hiddenLayerErrorsMatrix = {}'.format( self.hiddenLayerErrorsMatrix ) )
#		print( '           self.hiddenLayerDeltaErrorsMatrix = {}'.format( self.hiddenLayerDeltaErrorsMatrix ) )		

		#	DONE :: calculate errors and delta errors
		####################################################################
		
		####################################################################
		#	calculate delta weights

		#	calculate delta weights at output layer
		self.outputDeltaWeightsMatrix = learningRate * forwardPropagator.outputsMatrixHiddenLayerNeurons.T.dot( 
																			self.outputDeltaErrorsMatrix )
		
		#	calculate delta weights at hidden layer
		self.hiddenLayerDeltaWeightsMatrix = learningRate * forwardPropagator.inputsMatrix.T.dot( 
																			self.hiddenLayerDeltaErrorsMatrix )
		
		
#		print( '           self.hiddenLayerDeltaWeightsMatrix = {}'.format( self.hiddenLayerDeltaWeightsMatrix ) )
#		print( '           self.outputDeltaWeightsMatrix = {}'.format( self.outputDeltaWeightsMatrix ) )		

	def calculateRmsError( self ):
		''' calculate error '''
		return numpy.sqrt( numpy.mean( numpy.power( self.outputErrorsMatrix, 2 ) ) )
		
	
