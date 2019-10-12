# -*- coding: utf-8 -*-
"""
Created on 2019-05-29 18:44:15 (copy from test_core)

@author: Carsten Knoll
"""
from assimulo.solvers import IDA # Imports the solver IDA from Assimulo

import sympy as sp

import numpy as np

import symbtools as st


try:
    import control
except ImportError:
    control = None

import unittest


# noinspection PyShadowingNames,PyPep8Naming,PySetFunctionToLiteral
class SymbToolsTest(unittest.TestCase):

    def setUp(self):
        st.init_attribute_store(reinit=True)


    def test_integrate_with_time_derivs(self):
        t = sp.Symbol("t")
        x1, x2 = xx = st.symb_vector("x1, x2")
        xdot1, xdot2 = xxd = st.time_deriv(xx, xx)

        z = xdot1 - 4*xdot2

        res = st.smart_integrate(z, t)

        self.assertEqual(res, x1 - 4*x2)
