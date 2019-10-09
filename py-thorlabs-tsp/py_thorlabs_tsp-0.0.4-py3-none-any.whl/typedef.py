# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.typedef.py

This file contains type definitions used by the TSP01B DLL.

The definitions are taken from the
"IVI Foundation/WinNT/TLTSPB/Typelib/TLTSPB.odl". Only the type later
used in the code are defined here.

Author: Dima Pustakhod
Copyright: TU/e

"""
from ctypes import c_long, c_bool, c_char_p, c_short, c_double
from ctypes import create_string_buffer

ViSession = c_long
ViRsrc = c_char_p
ViStatus = c_long

ViBoolean = c_bool

ViInt16 = c_short
ViUInt16 = c_short
ViInt32 = c_long
ViUInt32 = c_long

ViReal64 = c_double

ViChar_arr = create_string_buffer
