#__author__ = "magnelPy"
#__email__= "ruben.vancoile@ugent.be"
#__date__= "2018-10-11"

####################
## MODULE IMPORTS ##
####################

import numpy as np
import scipy.stats as stats

##############
## FUNCTION ##
##############

def LHS(N, K, RedCor = False, MidPoint = False ):
	#------------------------------------------------------------------------------------------------------------
	# This function generates a Latin Hypercube consisting of N realizations of each of the K random variables
	#
	# Input:
	# 	N = the number of realizations/samples
	# 	K = the number of random variables
	# 	RedCor = switch the option to reduce spurious correlation on/off (True/False)
	#	MidPoint = switch the option to take the midpoint value of each interval (True/False)
	#
	# Output:
	#	numpy.ndarray : NxK array with LHS realizations (r-values between 0 and 1)
	# 
	# Procedure based on:
	# Olsson A., Sandberg G. & Dahlblom O. (2013) On Latin Hypercube Sampling for structural reliability analysis
	#     Structural Safety 25, pp 47-68
	#
	# Wouter Botte - 2017
	#------------------------------------------------------------------------------------------------------------

	if not isinstance(N, int ):
		print("________________________________________________________________________________")
		print("ERROR: the number of realizations N should be an integer")
		print("________________________________________________________________________________")
		return None
	if not isinstance(K, int ):
		print("________________________________________________________________________________")
		print("ERROR: the number of variables K should be an integer")
		print("________________________________________________________________________________")
		return None

	# Generate the matrix P containing K columns with random permutations of 1,...,N
	matrix = [ [ i for i in range(1, N + 1) ] for j in range(K) ]
	matrix = [ np.random.permutation( matrix[i] ) for i in range( len(matrix) ) ]
	P = np.transpose(matrix)

	# Reduction of spurious correlation if necessary
	if RedCor:
		if N < K:
			print("________________________________________________________________________________")
			print("ERROR: The number of realizations N is less than the number of variables K")
			print("	   In case of spurious correlation reduction N should be higher than K")
			print("________________________________________________________________________________")
			return None
		else:
			Y = np.array([ [ stats.norm.ppf(float(P[i][j])/(N + 1)) for j in range(K) ] for i in range(N)])
			covY = np.cov(np.transpose(Y))
			L = np.linalg.cholesky(covY)
			Ystar = np.dot(Y, np.transpose(np.linalg.inv(L)))
			Pstar = np.transpose(np.array([ [sorted(Ystar[:,i]).index(v) + 1 for v in Ystar[:,i]] for i in range(K)]))
			P = Pstar

	# Generate the matrix R of independent random numbers from the uniform distribution
	if MidPoint: R=0.5
	else: R = np.array(np.random.uniform(size = (N,K)))

	# Generate sampling plan S
	S = 1./N*(P-R)
	return S


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	N=10
	K=4
	Z=LHS(N,K,True,True)
	print(Z)
	print(type(Z))