"""Fire definition

Notes
-----
The FireCurve module supports definition of temperature-time curves for SFE.
"""

#############
## IMPORTS ##
#############

import numpy as np


############
## MODULE ##
############

def ISO834(time):
	""" Return ISO834 gas temperature at specified times

	Parameters
	----------
	time :	np.array
		array of time instants [min]

	Returns
	-------
	fire :	np.array
		array of gas temperatures for time [C]

	Reference
	---------
	EN 1991-1-2:2002. Eurocode 1: Actions on structures - Part 1-2:
		General actions - Actions on structures exposed to fire, 3.2.1 (p24) 

	Examples
	--------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> time = np.arange(0,120+1,1)
	>>> fire = sfe.FireCurve.ISO834(time)
	>>> print(np.array([time[[0,30,60,90,120]],
		np.around(fire[[0,30,60,90,120]],0)]))
	[[   0.   30.   60.   90.  120.]
 	[  20.  842.  945. 1006. 1049.]]
	"""
	return 20+345*np.log10(8*time+1)

#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	print("testing")

