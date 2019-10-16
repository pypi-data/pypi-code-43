#############################################################################
#                                                                           #
#    PyMassSpec software for processing of mass-spectrometry data           #
#    Copyright (C) 2019 Dominic Davis-Foster                                #
#                                                                           #
#    This program is free software; you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License version 2 as      #
#    published by the Free Software Foundation.                             #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program; if not, write to the Free Software            #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.              #
#                                                                           #
#############################################################################

import pytest
from tests.constants import *

from pyms.IntensityMatrix import IntensityMatrix
from pyms.IonChromatogram import IonChromatogram
from pyms.TopHat import tophat, tophat_im


def test_topHat(tic):
	assert isinstance(tic, IonChromatogram)
	
	# apply noise smoothing and baseline correction
	tic2 = tophat(tic, struct="1.5m")
	assert isinstance(tic2, IonChromatogram)
	
	tic3 = tophat(tic, struct=None)
	assert isinstance(tic3, IonChromatogram)

	tic4 = tophat(tic, struct=1234)
	assert isinstance(tic4, IonChromatogram)
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_tuple]:
		with pytest.raises(TypeError):
			tophat(type, "1m")
	for type in [test_float, test_list_ints, test_list_strs, test_tuple]:
		with pytest.raises(TypeError):
			tophat(tic, type)
	for type in [test_string]:
		with pytest.raises(ValueError):
			tophat(tic, type)
		

def test_tophat_im(im):
	# Use TopHat baseline correction on all IC's in the IM
	im_base_corr = tophat_im(im, struct="1.5m")
	assert isinstance(im_base_corr, IntensityMatrix)
	
	# find the IC for derivatisation product ion before smoothing
	ic = im.get_ic_at_index(73)
	assert isinstance(ic, IonChromatogram)
	
	# find the IC for derivatisation product ion after smoothing
	ic_base_corr = im_base_corr.get_ic_at_index(73)
	assert isinstance(ic_base_corr, IonChromatogram)
	
	# Errors
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_tuple]:
		with pytest.raises(TypeError):
			tophat_im(type, "1m")
	for type in [test_float, test_list_ints, test_list_strs, test_tuple]:
		with pytest.raises(TypeError):
			tophat_im(im, type)
	for type in [test_string]:
		with pytest.raises(ValueError):
			tophat_im(im, type)

# TODO:
# ic.write("output/ic.dat",minutes=True)
# ic_base_corr.write("output/ic_smooth.dat",minutes=True)
# save smoothed/baseline corrected TIC
# tic.write("output/tic.dat",minutes=True)
# tic1.write("output/tic_smooth.dat",minutes=True)
# tic2.write("output/tic_smooth_bc.dat",minutes=True)



