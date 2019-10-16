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
import copy

from pyms.Experiment  import Experiment
from pyms.Experiment import load_expr, read_expr_list, store_expr
from pyms.Peak.Class import Peak


def test_Experiment(expr, filtered_peak_list):
	assert isinstance(expr, Experiment)
	# Errors
	for type in [test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			Experiment(type, filtered_peak_list)
			
	for type in [test_string, test_int, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			Experiment(test_string, type)
	
	
def test_equality(expr):
	assert expr == Experiment(expr.expr_code, expr.peak_list)
	assert expr != Experiment(test_string, expr.peak_list)
	assert expr != test_float
	assert expr != test_int
	assert expr != test_string
	assert expr != test_list_ints
	assert expr != test_list_strs
	assert expr != test_dict
	assert expr != test_tuple


def test_len(expr):
	assert len(expr) == 641


def test_get_expr_code(expr):
	with pytest.warns(DeprecationWarning):
		expr.get_expr_code()

		
def test_expr_code(expr):
	assert isinstance(expr.expr_code, str)
	assert expr.expr_code == "ELEY_1_SUBTRACT"


def test_get_peak_list(expr):
	with pytest.warns(DeprecationWarning):
		expr.get_peak_list()


def test_peak_list(expr, filtered_peak_list):
	assert isinstance(expr.peak_list, list)
	assert isinstance(expr.peak_list[0], Peak)
	assert expr.peak_list == filtered_peak_list


def test_sele_rt_range(expr, filtered_peak_list):
	expr = copy.copy(expr)
	
	expr.sele_rt_range(["6.5m", "21m"])
	assert expr.peak_list != filtered_peak_list

	for type in [test_string, test_int, test_float, test_dict]:
		with pytest.raises(TypeError):
			expr.sele_rt_range(type)

	for type in [test_list_ints, test_list_strs]:
		with pytest.raises(ValueError):
			expr.sele_rt_range(type)


def test_store_expr(expr, outputdir):
	with pytest.warns(DeprecationWarning):
		store_expr(str(outputdir/"ELEY_1_SUBTRACT_DEPRECATION.expr"), expr)

	for type in [test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.warns(DeprecationWarning):
			with pytest.raises(TypeError):
				store_expr(type, expr)

	for type in [test_int, test_float, test_string, test_dict, test_list_ints, test_list_strs]:
		with pytest.warns(DeprecationWarning):
			with pytest.raises(TypeError):
				store_expr(test_string, type)


def test_store(expr, outputdir):
	expr.store(outputdir/"ELEY_1_SUBTRACT.expr")

	for type in [test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			expr.store(type)


def test_load_expr(filtered_peak_list, datadir, outputdir):
	expr = load_expr(outputdir/"ELEY_1_SUBTRACT.expr")
	assert isinstance(expr, Experiment)
	
	assert isinstance(expr.expr_code, str)
	assert expr.expr_code == "ELEY_1_SUBTRACT"

	assert isinstance(expr.peak_list, list)
	assert isinstance(expr.peak_list[0], Peak)
	
	assert expr.peak_list == filtered_peak_list
	expr.sele_rt_range(["6.5m", "21m"])

	# Errors
	for type in [test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			load_expr(type)

	with pytest.raises(IOError):
		load_expr(datadir/"non-existent.expr")
	with pytest.raises(IOError):
		load_expr(datadir/"not-an-experiment.expr")


def test_read_expr_list(filtered_peak_list, datadir):
	expr_list = read_expr_list(datadir/"read_expr_list.txt")
	assert isinstance(expr_list, list)
	assert isinstance(expr_list[0], Experiment)
	
	expr = expr_list[0]
	assert isinstance(expr.expr_code, str)
	assert expr.expr_code == "ELEY_1_SUBTRACT"

	assert isinstance(expr.peak_list, list)
	assert isinstance(expr.peak_list[0], Peak)
	assert expr.peak_list == filtered_peak_list

	expr.sele_rt_range(["6.5m", "21m"])

	# Errors
	for type in [test_int, test_float, test_dict, test_list_ints, test_list_strs]:
		with pytest.raises(TypeError):
			read_expr_list(type)
	
	with pytest.raises(IOError):
		read_expr_list("non-existent.expr")
	with pytest.raises((IOError, UnicodeDecodeError)):
		read_expr_list("not-an-experiment.expr")
	with pytest.raises(IOError):
		read_expr_list("__init__.py")

