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

class Perceptron:
	''' this class designed for has only one hidden layer and one output layer
			with whatever perceptron inside each layers
		this class wil store the weights and bias matrix for hidden layer and output layer
	'''
	
	
	def __init__( self, numInputs, numHiddenLayerNeurons, numOutputs, numSamples ):
		
		#	store number of inputs, hidden layer nuerons and outputs
		self.numInputs = numInputs
		self.numHiddenLayerNeurons = numHiddenLayerNeurons
		self.numOutputs = numOutputs
		
		#	store number of samples
		self.numSamples = numSamples
		
		#	weights matrix for hidden layer and output layer
		self.hiddenLayerWeightsMatrix = None
		self.outputLayerWeightsMatrix = None
		
		#	bias matrix for hidden layer and output layer
		self.hiddenLayerBiasMatrix = None
		self.outputLayerBiasMatrix = None
		
		#	call initialize weights and bias matrix
		self.initializeAndRandomizeWeightsAndBiasMatrix()
		
	def initializeAndRandomizeWeightsAndBiasMatrix( self ):
		''' initialize the hiddne layer and ouput layer weights matrix
				and ramdomize weights and bias matrix
			note that ramdomize weight from -1 to 1
		'''
		
		#	initialize and randomize weights and bias matrix for hidden layers
		#		weights matrix from -1 to 1
		self.hiddenLayerWeightsMatrix = 2 * numpy.random.random( ( self.numInputs, self.numHiddenLayerNeurons ) ) - 1
		self.hiddenLayerWeightsMatrix = numpy.vstack( [ self.hiddenLayerWeightsMatrix, [ 0 for i in xrange( self.numHiddenLayerNeurons ) ] ] )
		
#		#		bias matrix to be 0
#		self.hiddenLayerBiasMatrix = numpy.zeros( ( 1, self.numHiddenLayerNeurons ) )
		
		#	initialize and randomize weights and bias matrix for output layers
		#		weights matrix from -1 to 1
		self.outputLayerWeightsMatrix = 2 * numpy.random.random( ( self.numHiddenLayerNeurons, self.numOutputs ) ) - 1
		self.outputLayerWeightsMatrix = numpy.vstack( [ self.outputLayerWeightsMatrix, [ 0 for i in xrange( self.numOutputs ) ] ] )
		
#		#		bias matrix to be 0
#		self.outputLayerBiasMatrix = numpy.zeros( ( 1, self.numOutputs ) )
	
	def applyDeltaWeights( self, backwardPropagator ):
		''' apply the delta weights this this hidden layer neuron weights and output weights
		'''
		
		#	apply delta weights at hidden layer
		self.hiddenLayerWeightsMatrix += backwardPropagator.hiddenLayerDeltaWeightsMatrix

		#	apply delta weights at output layer
		self.outputLayerWeightsMatrix += backwardPropagator.outputDeltaWeightsMatrix
	
