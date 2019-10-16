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

from pyms.Noise.Analysis import window_analyzer


def test_window_anlyzer(tic):
	noise_estimate = window_analyzer(tic, rand_seed=test_int)
	assert noise_estimate == 22524.833209785025
	
	assert isinstance(noise_estimate, float)
	assert isinstance(window_analyzer(tic), float)
	assert isinstance(window_analyzer(tic, rand_seed=test_string), float)
	assert isinstance(window_analyzer(tic, rand_seed=test_float), float)
	
	for type in [test_string, test_int, test_float, test_list_ints, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			window_analyzer(type)
	
	for type in [test_list_ints, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			window_analyzer(tic, rand_seed=type)
	for type in [test_float, test_list_ints, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			window_analyzer(tic, window=type)
	for type in [test_string, test_float, test_list_ints, test_list_strs, test_dict]:
		with pytest.raises(TypeError):
			window_analyzer(tic, n_windows=type)
