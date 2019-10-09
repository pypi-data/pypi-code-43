# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.constants.py

This file contains constants used by the TSP01B DLL.

The constant definitions are taken from multiple files provided
by Thorlabs as a part of TSP01 software.

Author: Dima Pustakhod
Copyright: TU/e

"""
from ctypes import c_long

# from "IVI Foundation/WinNT/TLTSPB/Typelib/TLTSPB.odl"
# -----------------------------------------------------
VI_NULL = c_long(0)

VI_SUCCESS = 0x0


# from "IVI Foundation/Win64/Include/TLTSPB.h"
# --------------------------------------------
TLTSP_TEMPER_CHANNEL_1 = 11
TLTSP_TEMPER_CHANNEL_2 = 12
TLTSP_TEMPER_CHANNEL_3 = 13

# from "IVI Foundation/Win64/Include/TLTSP_Defines.h"
# ---------------------------------------------------
# Buffers
TLTSP_BUFFER_SIZE = 256  # General buffer size
TLTSP_ERR_DESCR_BUFFER_SIZE = 512  # Buffer size for error messages

# Attributes
TLTSP_ATTR_SET_VAL = 0
TLTSP_ATTR_MIN_VAL = 1
TLTSP_ATTR_MAX_VAL = 2
TLTSP_ATTR_DFLT_VAL = 3
