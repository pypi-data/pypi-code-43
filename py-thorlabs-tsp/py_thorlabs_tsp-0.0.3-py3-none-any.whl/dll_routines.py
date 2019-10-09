# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.dll_routines.py

This file contains routines to load DLL and call functions from it.

Author: Dima Pustakhod
Copyright: TU/e
"""
import ctypes
import inspect
import os
from platform import architecture, system


PREFIX = 'TLTSPB'


def _load_dll() -> ctypes.WinDLL:
    """Check the supposed locations for the DLL and load it.

    Returns
    -------
        ctypes.WinDLL
    """
    syst: str = system()
    bits: str = architecture()[0]

    if syst != 'Windows':
        raise NotImplementedError(
            f'This package was not tested on {syst}! Please contact '
            'the author if you would like to do this.')

    dll = None
    if bits == '32bit':
        paths = (
            'C:/Program Files/IVI Foundation/VISA/WinNT/Bin/',
            'C:/Program Files/Thorlabs/TSP01/'
        )
        dll_name = 'TLTSPB_32.dll'

        for path in paths:
            if os.path.exists(path+dll_name):
                dll = ctypes.WinDLL(path + dll_name)
    elif bits == '64bit':
        paths = (
            'C:/Program Files/IVI Foundation/Win64/Bin/',
        )
        dll_name = 'TLTSPB_64.dll'
        for path in paths:
            if os.path.exists(path+dll_name):
                dll = ctypes.WinDLL(path + dll_name)
    else:
        raise UserWarning(f'The current OS bitness ({bits}) is not supported.')

    if not dll:
        raise UserWarning(f'The TLTSPB_xx.DLL for the current OS ({system}, '
                          f'{bits}) not found. Please check if the TSP01 '
                          f'application is installed properly.')

    return dll


_dll = _load_dll()


def _get_dll_fcn_name(prefix: str, level_up: int = 1) -> str:
    """Get the name of the function to be called.

    If _get_dll_fcn_name() is called from the function f(), then it
    returns prefix + 'f' (with level_up=1).

    Parameters
    ----------
    prefix : str
        prefix to be added to the caller function name.
    level_up : int
        Defines how far up in the stack to look. 0 means this function
        itself. 1 means the name of the caller function. 2 means the
        function calling the caller function, etc. Default is 1.

    Returns
    -------
    str
        name of the DLL function to be called.
    """
    fcn_name = inspect.stack()[level_up][3]
    dll_fcn_name = prefix + fcn_name
    return dll_fcn_name


def _get_fcn_from_dll(dll: ctypes.WinDLL, level_up: int = 1):
    """Get the function from the DLL.

    The name of the function is determined by the caller function's name.
    See _get_dll_fcn_name().

    Parameters
    ----------
    dll : ctypes.WinDLL
        loaded DLL library
    level_up : int
        Defines how far up in the stack to look. 0 means this function
        itself. 1 means the name of the caller function. 2 means the
        function calling the caller function, etc. Default is 1.

    """
    # increase level_up because we are already deeper than the caller
    # function by 1
    dll_fcn_name = _get_dll_fcn_name(PREFIX, level_up=level_up + 1)
    fcn = getattr(dll, dll_fcn_name)
    return fcn


def _call_dll_fcn(*args, **kwargs) -> int:
    """Call the DLL-function.

    The function to be called is determined by the caller function's name.
    See _get_fcn_from_dll().

    Returns
    -------
    int
        result of the function call
    """
    fcn = _get_fcn_from_dll(_dll, 2)
    status = fcn(*args, **kwargs)
    return status
