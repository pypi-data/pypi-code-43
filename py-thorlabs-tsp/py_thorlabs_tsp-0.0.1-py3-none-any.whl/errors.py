# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.thorlabs_tsp01b.py

This file implements a class to control Thorlabs TSP01B sensor.

It wraps limited set of low-level functions in a single class and
provides error processing.

Author: Dima Pustakhod
Copyright: TU/e
"""
from typing import Optional

from . import _errorMessage


class ThorlabsTsp01BException(Exception):
    """Base exception for Thorlabs TSP01B sensor
    """
    pass


def _process_error(instr_handle: int, error_code: int, fcn: Optional[str] = ''):
    if error_code:
        e, err_descr = _errorMessage(instr_handle, error_code)
        if e:
            raise ThorlabsTsp01BException(
                'Error obtaining error description for error'
                'code 0x{:x}: 0x{:x}.'.format(error_code, e)
            )
        else:
            raise ThorlabsTsp01BException(
                'Error 0x{:x} when calling {}: {}.'.format(
                    error_code, fcn, err_descr
                )
            )
