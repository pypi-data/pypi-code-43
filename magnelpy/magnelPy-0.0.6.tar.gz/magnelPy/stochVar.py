#__author__ = "magnelPy"
# test 1

#--------------------------------------------------------------------------------------------------------
# Standard formatting stochastic variables
#--------------------------------------------------------------------------------------------------------

####################
## MODULE IMPORTS ##
####################

import numpy as np

##############
## FUNCTION ##
##############

def createStochVar(name='',dist='normal',mean=0.,std=1.,dim='[-]',comment='',theta1=None,theta2=None):
	## standard formatting of stochastic variables ##
	# name = name of stochastic variable
	# dist = distribution type
	# mean = mean value
	# std = standard deviation
	# dim = dimension
	# comment = free notes
	# theta1 = first additional parameter - when appropriate - can be improved
	# theta2 = second additional parameter - when appropriate - can be improved
	return {'name':name,'dist':dist,'dim':dim,'m':mean,'s':std,'info':comment,'theta1':theta1,'theta2':theta2}




##################
## AUX FUNCTION ##
##################


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	### Concrete slab ###
	cover = 0.035   # concrete cover [m]
	sig_cover = 0.010 # st.dev. of concrete cover [m]
	rebar = 0.01  #rebar diameter [m]
	dist = 0.1  #distance between rebars [m]
	w = 1.    #slab width [m]	

	As=createStochVar(dist='normal',mean=0.25*(np.pi)*rebar**2*(w/dist)*1.02,std=0.02*0.25*(np.pi)*rebar**2*(w/dist)*1.02,dim='[m2]',name='As [m2]')
	fck=30; Vfc=0.15 # [MPa]; [-]
	fc=createStochVar(dist='lognormal',mean=fck/(1-2*Vfc),std=fck/(1-2*Vfc)*Vfc,dim='[MPa]',name='fc20 [MPa]')

	StochVarDict={'As':As,'fc':fc}

	nameList=[StochVarDict[key]['name'] for key in StochVarDict.keys()]

	print(StochVarDict.keys())    
