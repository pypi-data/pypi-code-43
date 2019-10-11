#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Uncertainty propagation with Monte-Carlo method

'''

import numpy as np

from astools.sinout import write_fits

def calunc(data, NAXIS, filOUT=None, hdr=None, wave=None):
	'''
	Calculate uncertainties
	
	--- INPUT ---
	data        data
	NAXIS       should be coherent with data shape
	filOUT      defaut no output fits file
	hdr         fits file header
	wave        wavelengths if 3D
	--- OUTPUT ---
	err         one dim less than data
	'''
	## detect dimension
	dim = np.size(NAXIS)
	if dim==1:
		err = np.full(NAXIS[0], np.nan)
		for i in range(NAXIS[0]):
			err[i] = np.nanstd(data[:,i], ddof=1)
	elif dim==2:
		err = np.full((NAXIS[1], NAXIS[0]), np.nan)
		for i in range(NAXIS[0]):
			for j in range(NAXIS[1]):
				err[j,i] = np.nanstd(data[:,j,i], ddof=1)
	else:
		err = np.full((NAXIS[2], NAXIS[1], NAXIS[0]), np.nan)
		for i in range(NAXIS[0]):
			for j in range(NAXIS[1]):
				for k in range(NAXIS[2]):
					err[k,j,i] = np.nanstd(data[:,k,j,i], ddof=1)

	if filOUT!=None:
		comment = "Monte-Carlo propagated uncertainty file."
		write_fits(filOUT, hdr=hdr, data=err, wave=wave, COMMENT=comment)
	
	return err
