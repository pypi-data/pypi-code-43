#__author__ = "magnelPy"
#__email__= "ruben.vancoile@ugent.be"
#__date__= "2018-10-11"

####################
## MODULE IMPORTS ##
####################

import numpy as np
import scipy.stats as stats
import sympy as sy
import pandas as pd
from copy import deepcopy

# from magnelPy import statFunc
from magnelPy.admin import df_writeToExcel
from magnelPy.stochVar import createStochVar


import sys
magnelpyPath="C:/Users/rvcoile/Google Drive/Research/Codes/MagnelPy/magnelPy"
directory=magnelpyPath
sys.path.append(directory)
import statFunc

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

def MonteCarlo(limitstate,ParameterDict,nMC,method='MCS'):
	#------------------------------------------------------------------------------------------------------------
	# Limit state evaluation - WIP
	#
	# Input:
	# 	varDict = Dictionary with function parameters (in function of distribution)
	#		'name' = name of parameter: 'X'
	#		'Dist' = Distribution type: one of the following:
	#				'N' : Normal
	#				'LN' : Lognormal
	#				'MixedLN' : Mixed Lognormal (probability weighted contributions of LN constituents)
	#				'G' : Gumbel
	#				'DET' : Deterministic
	#		'm' = mean value X - or pd.Series of constituent mean values
	#		's' = standard deviation X - or pd.Series of constituent standard deviations
	#		'P' = pd.Series with probabilities of constituents (cfr. MixedLN)
	#		'info' = further notes
	#	rArray = np.array (or commutable) with quantile realizations ri (0,1)
	#
	# Output:
	#	parameter realizations xi
	# rvcpy - 2017
	#------------------------------------------------------------------------------------------------------------
	# performs crude Monte Carlo simulation
	# input
	# * limitstate: symbolic limit state function
	# * ParameterDict: dictionary of all parameters, including probabilistic discription
	# * nMC: number of simulations
	# output
	# * array of limit state evaluations, DataFrame with parameter values and limit state valuation, DataFrame with random values

	## create MCS array random values
	symbolList=limitstate.atoms(sy.Symbol)
	nvar=len(symbolList)
	rMatrix=np.random.rand(nMC,nvar)

	## calculate MCS array random realizations
	xMatrix=np.zeros((nMC,nvar))
	# indexing in the ParameterDict - general indexing  
	indexDict={}
	for key in ParameterDict:
		indexDict[ParameterDict[key]['name']]=key
	# random realization per parameter
	varOrder=[]
	for i,X in enumerate(symbolList):
		# save order for printing lists
		var=X.name
		varOrder.append(var)
		# collect Dict (stochastic) variable
		localDict=ParameterDict[indexDict[var]]
		xMatrix[:,i]=ParameterRealization_r(localDict,rMatrix[:,i])

	## evaluate limit state
	limitstateEval = sy.lambdify(tuple(varOrder), limitstate, 'numpy')
	lsEvalList=LS_evaluation(limitstateEval,nvar,xMatrix)


	## output
	# outR first, before appending the varOrder...
	outR=pd.DataFrame(rMatrix,columns=varOrder)
	# set output - variable realizations + limit state evaluation
	lsEvalList=np.reshape(lsEvalList,(nMC,1))
	full=np.concatenate((xMatrix,lsEvalList),axis=1)
	varOrder.append('LS')
	outX=pd.DataFrame(full,columns=varOrder)

	return lsEvalList, outX, outR

def MCS_var(varDict,n):
	#------------------------------------------------------------------------------------------------------------
	# Return n realizations of stochastic variable
	#
	# Input:
	# 	varDict = Dictionary with function parameters (in function of distribution) - cfr. standard format
	#	n = number of realizations
	# Output:
	#	pd.Series of realizations
	# concept Generaterandom.py TTH 11.2018
	#------------------------------------------------------------------------------------------------------------

	r=np.random.rand(n) # ri-values (random quantiles)
	return pd.Series(ParameterRealization_r(varDict,r),np.arange(n))


def Taylor(limitstate,ParameterDict):
	# Taylor approximation of mean value and standard deviation
	# input
	# * limitstate: symbolic limit state function
	# * ParameterDict: dictionary of all parameters, including probabilistic discription
	# output
	# * mean value, standard deviation

	# ^cfr. rvcpy - probabcalc.py 2017-11-24: created

	# list of symbols in limitstate
	symbolList=limitstate.atoms(sy.Symbol)
	nvar=len(symbolList)
	xMatrix=np.zeros((2,nvar)) 	# array mean values and standard deviations

	# indexing in the ParameterDict - general indexing  
	indexDict={}
	for key in ParameterDict:
		indexDict[ParameterDict[key]['name']]=key

	# values per parameter
	varOrder=[]
	lsList=[]
	for i,X in enumerate(symbolList):
		# save order for printing lists
		var=X.name
		varOrder.append(var)
		# collect Dict (stochastic) variable
		localDict=ParameterDict[indexDict[var]]
		xMatrix[:,i]=[localDict['m'],localDict['s']]
		# take derivative of limitstate function
		ls=sy.diff(limitstate,X)
		lsList.append(ls)

	## evaluate limit state - mean value
	limitstateEval = sy.lambdify(tuple(varOrder), limitstate, 'numpy')	
	m=LS_evaluation(limitstateEval,nvar,xMatrix); m=m[0]

	s2=0
	for i in np.arange(nvar):
		functionEval = sy.lambdify(tuple(varOrder), lsList[i], 'numpy')	
		d=LS_evaluation(functionEval,nvar,xMatrix)
		if type(d)!=int: d=d[0]
		s2=s2+d**2*xMatrix[1,i]**2

	return m,np.sqrt(s2)

def MDRMG(varDict,L=5,outdir='TMP'):
	#------------------------------------------------------------------------------------------------------------
	# MDRM-G input samples
	#
	# Input:
	# 	varDict = Dictionary with parameters stoch variables (in function of distribution) - cfr. standard format
	#	L = Gauss integration order
	# Output:
	#	pd.DataFrame of input values
	#	pd.DataFrame of sampling scheme
	# concept MaxEnt_sampling.py RVC 06.2018
	#------------------------------------------------------------------------------------------------------------

	## input assessment ##
	n = len(varDict.keys()) # number of stochastic variables - does not correct for DET variables
	if L % 2 == 0:
		print("L is even - recommended to apply odd number of integration points for improved accuracy at same cost")
	else:
		nSim=(L-1)*n+1 # number of sample points

	## Gauss points and quantiles X, considering L ##
	points=GaussPoints(L)
	r_realizations=statFunc.F_Normal(points,0,1) # quantiles corresponding with Gauss points
	r_realizations=r_realizations.flatten()

	## realizations per variable ##
	GaussPoint_df=pd.DataFrame(index=np.arange(1,L+1))
	varList=pd.Series(index=np.arange(n)+1)
	for i,var in enumerate(varDict):
		l=i+1 # stochvar number sampling scheme
		stochvar=varDict[var]
		samplepoints=ParameterRealization_r(stochvar,r_realizations)
		GaussPoint_df[l]=samplepoints
		varList[l]=stochvar['name']

	## assign in sampling scheme ##
	samplingScheme=GaussSampleScheme(L,n,nSim)
	samples_modelInput=CalculationPoints(samplingScheme,GaussPoint_df,nSim)

	## output reference
	name='MDRMGauss_samples'

	## print results
	reference=deepcopy(samples_modelInput)
	reference.columns=varList[reference.columns]

	df_writeToExcel([samples_modelInput,samplingScheme,reference],outdir+'/'+name,['modelInput','samplingScheme','modelInput_named'])

	# file reference copy - cfr. MaxEnt_sampling.py when defining stochVar from *.xlsx
	# # file stochastic variable reference path for future reference
	# text_file = open(outdir+"/REF_input_stoch.txt", "w")
	# text_file.write("Stochastic variable reference file:\n%s\n\nsheet:\n%s" %(filename,sheet)) 
	# text_file.close()

##################
## AUX FUNCTION ##
##################

def ParameterRealization_r(varDict,rArray):
	#------------------------------------------------------------------------------------------------------------
	# Realizations stochastic variable
	#
	# Input:
	# 	varDict = Dictionary with function parameters (in function of distribution)
	#		'name' = name of parameter: 'X'
	#		'Dist' = Distribution type: one of the following:
	#				'N' : Normal
	#				'LN' : Lognormal
	#				'MixedLN' : Mixed Lognormal (probability weighted contributions of LN constituents)
	#				'G' : Gumbel
	#				'DET' : Deterministic
	#		'm' = mean value X - or 'mi' = pd.Series of constituent mean values
	#		's' = standard deviation X - or 'si' = pd.Series of constituent standard deviations
	#		'P' = pd.Series with probabilities of constituents (cfr. MixedLN)
	#		'info' = further notes
	#	rArray = np.array (or commutable) with quantile realizations ri (0,1)
	#
	# Output:
	#	parameter realizations xi
	# rvcpy - 2017
	#------------------------------------------------------------------------------------------------------------
	DistType=varDict['dist']
	if DistType=='normal':
		return statFunc.Finv_Normal(rArray,varDict['m'],varDict['s'])
	if DistType=='lognormal':
		return statFunc.Finv_Lognormal(rArray,varDict['m'],varDict['s'])
	if DistType=='mixedlognormal':
		return statFunc.Finv_MixedLN(rArray,varDict['mi'],varDict['si'],varDict['Pi'])
	if DistType=='gumbel':
		return statFunc.Finv_Gumbel(rArray,varDict['m'],varDict['s'])
	if DistType=='deterministic':
		return np.ones(np.shape(rArray))*varDict['m']
	if DistType=='beta':
		return statFunc.Finv_Beta_ab(rArray,varDict['m'],varDict['s'],varDict['theta1'],varDict['theta2'])
	if DistType=='gamma':
		return statFunc.Finv_Gamma(rArray,varDict['m'],varDict['s'])
	if DistType=='uniform':
		return statFunc.Finv_Uniform(rArray,varDict['theta1'],varDict['theta2'])
	if DistType=='weibull':
		return statFunc.Finv_Weibull(rArray,varDict['m'],varDict['s'])
	if DistType=='lognormal_truncated':
		return statFunc.Finv_Lognormal_truncated(rArray,varDict['m'],varDict['s'],varDict['theta1'])

def LS_evaluation(LS_eval,nvar,xMatrix):

	#
	### TO BE IMPROVED ###
	# a list can be unpacked by adding *
	# e.g. LS_eval(*xMatrix)
	# unclear what this will do what a 2D array...
	#

	# currently hardcoded number of subs
	# more Pythonic code? !?!?!?
	if nvar==1:
		lsEvalList=LS_eval(xMatrix[:,0])
	elif nvar==2:
		lsEvalList=LS_eval(xMatrix[:,0],xMatrix[:,1])
	elif nvar==3:
		lsEvalList=LS_eval(xMatrix[:,0],xMatrix[:,1],xMatrix[:,2])
	elif nvar==4:
		lsEvalList=LS_eval(xMatrix[:,0],xMatrix[:,1],xMatrix[:,2],xMatrix[:,3])
	elif nvar==5:
		lsEvalList=LS_eval(xMatrix[:,0],xMatrix[:,1],xMatrix[:,2],xMatrix[:,3],xMatrix[:,4])
	elif nvar==6:
		lsEvalList=LS_eval(xMatrix[:,0],xMatrix[:,1],xMatrix[:,2],xMatrix[:,3],xMatrix[:,4],xMatrix[:,5])
	## to be continued

	return lsEvalList

def GaussPoints(n):
	#------------------------------------------------------------------------------------------------------------
	#  "Probabilistic" Gauss Hermite integration points - option to add others
	#
	# Input:
	# 	n = order of Gauss integration
	#
	# Output:
	#	array of Gauss integration points
	#
	# rvc - 2015
	#------------------------------------------------------------------------------------------------------------

	## Traditional [Physicist] Gauss Hermite integration points
	if n==2:
		points=[-0.707106781187,0.707106781187]
	if n==3:
		points=[-1.22474487139,0.,1.22474487139]
	if n==4:
		points=[-1.65068012389,-0.524647623275,0.524647623275,1.65068012389]
	if n==5:
		points=[-2.02018287046,-0.958572464614,0.,0.958572464614,2.02018287046]
	if n==6:
		points=[-2.35060497367,-1.33584907401,-0.436077411928,0.436077411928,1.33584907401,2.35060497367]
	if n==7:
		points=[-2.65196135684,-1.67355162877,-0.816287882859,0.,0.816287882859,1.67355162877,2.65196135684]
	if n==8:
		points=[-2.93063742026,-1.9816567567,-1.15719371245,-0.381186990207,0.381186990207,1.15719371245,1.9816567567,2.93063742026]
	if n==9:
		points=[-3.19099320178,-2.26658058453,-1.46855328922,-0.723551018753,0.,0.723551018753,1.46855328922,2.26658058453,3.19099320178]
	if n==10:
		points=[-3.43615911884,-2.53273167423,-1.7566836493,-1.03661082979,-0.342901327224,0.342901327224,1.03661082979,1.7566836493,2.53273167423,3.43615911884]
	if n==11:
		points=[-3.66847084656,-2.78329009978,-2.02594801583,-1.32655708449,-0.656809566882,0.,0.656809566882,1.32655708449,2.02594801583,2.78329009978,3.66847084656]
	if n==12:
		points=[-3.88972489787,-3.02063702512,-2.2795070805,-1.59768263515,-0.94778839124,-0.314240376254,0.314240376254,0.94778839124,1.59768263515,2.2795070805,3.02063702512,3.88972489787]

	if n==17:
		points=[-4.87134519367,-4.06194667588,-3.37893209114,-2.7577629157,-2.17350282667,-1.61292431422,-1.06764872574,-0.531633001343,0.,0.531633001343,1.06764872574,1.61292431422,2.17350282667,2.7577629157,3.37893209114,4.06194667588,4.87134519367]

	# multiplication sqrt(2) for "Probabilistic" Gauss-Hermite weights	
	points= [z * np.sqrt(2) for z in points] 
	PointsList=pd.DataFrame(points,index=np.arange(1,n+1,1),columns=['zj'])
	return PointsList 

def GaussSampleScheme(L,n,nSim):

    # initialize
    scheme=pd.DataFrame(index=np.arange(1,nSim+1),columns=['j','l'])    

    for l in np.arange(n+1):

        if l==0:
            scheme.loc[1,:]=[0,0] # starting entry as median value realization
        else:
            scheme.loc[2+4*(l-1):2+4*l-1,:]=[[1,l],[2,l],[4,l],[5,l]]    

    return scheme


def CalculationPoints(samplingScheme,GaussPoint_df,nSim):

    modelInput=pd.DataFrame(index=np.arange(1,nSim+1),columns=GaussPoint_df.columns)

    # initialize median values for all parameter realizations
    for var in modelInput.columns:
        modelInput[var]=GaussPoint_df.loc[3,var]

    # correct on every line the single modified Gauss point
    for i in modelInput.index:

        # j,l realization
        [j,l]=samplingScheme.loc[i,:]

        # assignment
        if l!=0: # 0-value corresponds with median point
            modelInput.loc[i,l]=GaussPoint_df.loc[j,l]

    return modelInput


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	### test LHS ###
	# N=10000
	# K=8
	# Z=LHS(N,K,True,True)

	# LHSpath='C:\\Users\\rvcoile\\Google Drive\\Research\\Codes\\refValues\\LHScenter_10000_8var.xlsx'
	# sheet='r'
	
	# out=pd.DataFrame(Z,index=np.arange(N),columns=np.arange(K))

	# df_writeToExcel(out,LHSpath,sheet)

	### test random realization ###
    # Concrete slab #
    cover = 0.035   # concrete cover [m]
    sig_cover = 0.010 # st.dev. of concrete cover [m]
    rebar = 0.01  #rebar diameter [m]
    dist = 0.1  #distance between rebars [m]
    w = 1.    #slab width [m] 
    As=createStochVar(dist='normal',mean=0.25*(np.pi)*rebar**2*(w/dist)*1.02,std=0.02*0.25*(np.pi)*rebar**2*(w/dist)*1.02,dim='[m2]',name='As [m2]')
    print(MCS_var(As,100))