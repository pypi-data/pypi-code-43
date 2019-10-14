# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

"""
Module that contains functions to work with win32
"""

import sys
import ctypes
import ctypes.wintypes

GWL_WNDPROC         = -4
GWL_HINSTANCE       = -6
GWL_HWNDPARENT      = -8
GWL_STYLE           = -16
GWL_EXSTYLE         = -20
GWL_USERDATA        = -21
GWL_ID              = -12

WS_BORDER	        = 0x800000
WS_CAPTION	        = 0xc00000
WS_CHILD	        = 0x40000000
WS_CHILDWINDOW	    = 0x40000000
WS_CLIPCHILDREN     = 0x2000000
WS_CLIPSIBLINGS     = 0x4000000
WS_DISABLED	        = 0x8000000
WS_DLGFRAME	        = 0x400000
WS_GROUP	        = 0x20000
WS_HSCROLL	        = 0x100000
WS_ICONIC	        = 0x20000000
WS_MAXIMIZE	        = 0x1000000
WS_MAXIMIZEBOX	    = 0x10000
WS_MINIMIZE	        = 0x20000000
WS_MINIMIZEBOX	    = 0x20000
WS_OVERLAPPED	    = 0
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_POPUP	        = 0x80000000
WS_POPUPWINDOW	    = 0x80880000
WS_SIZEBOX	        = 0x40000
WS_SYSMENU	        = 0x80000
WS_TABSTOP	        = 0x10000
WS_THICKFRAME	    = 0x40000
WS_TILED	        = 0
WS_TILEDWINDOW	    = 0xcf0000
WS_VISIBLE	        = 0x10000000
WS_VSCROLL	        = 0x200000


def to_hwnd(pycobject):
    """
    Convenience method to get a Windows Handle from a PySide WinID
    Based on http://srinikom.github.io/pyside-bz-archive/523.html
    @return A value equivalent to a void* that represents the Windows handle if one exists; None otherwise.
    """

    if type(pycobject) is long:
        # That specific case happen in maya 2017, here, we already have the hwnd so no further manipulation is needed
        return pycobject
    if sys.version_info[0] == 2:
        ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
        return ctypes.pythonapi.PyCObject_AsVoidPtr(pycobject)
    elif sys.version_info[0] == 3:
        ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object]
        return ctypes.pythonapi.PyCapsule_GetPointer(pycobject, None)


def set_owner(hwnd, hwnd_owner):
    """
    Changes the owner window of the given window
    :param hwnd:
    :param hwnd_owner:
    """

    _update_window = ctypes.windll.user32.UpdateWindow

    # WIN32 vs WIN64 - from a macro in winuser.h
    if ctypes.sizeof(ctypes.wintypes.HWND) == ctypes.sizeof(ctypes.c_long):
        _LONG = ctypes.wintypes.LONG
        _set_window_long = ctypes.windll.user32.SetWindowLongW
        _set_window_long.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.wintypes.LONG]
        _set_window_long.restype = ctypes.c_void_p
    elif ctypes.sizeof(ctypes.wintypes.HWND) == ctypes.sizeof(ctypes.c_longlong):
        _LONG = ctypes.wintypes.HWND
        _set_window_long = ctypes.windll.user32.SetWindowLongPtrW
        _set_window_long.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.wintypes.HWND]
        _set_window_long.restype = _LONG

    last_error = ctypes.set_last_error(0)
    try:
        result = _set_window_long(ctypes.wintypes.HWND(hwnd), ctypes.c_int(GWL_HWNDPARENT), _LONG(hwnd_owner))
    finally:
        last_error = ctypes.set_last_error(last_error)

    if not result and last_error:
        raise ctypes.WinError(last_error)

    _update_window(hwnd_owner)

    return result


def get_reg_key(registry, key, architecture=None):
    """
    Returns a _winreg hkey if found
    :param registry: str, registry to look in. HKEY_LOCAL_MACHINE for example
    :param key: str, key to open 'Software/Ubisoft/Test' for example
    :param architecture: variant, int || None, 32 or 64 bit. If None, default system architecture is used
    :return: _winreg handle object
    """

    import _winreg

    reg_key = None
    a_reg = _winreg.ConnectRegistry(None, getattr(_winreg, registry))
    if architecture == 32:
        sam = _winreg.KEY_WOW64_32KEY
    elif architecture == 64:
        sam = _winreg.KEY_WOW64_64KEY
    else:
        sam = 0
    try:
        reg_key = _winreg.OpenKey(a_reg, key, 0, _winreg.KEY_READ | sam)
    except WindowsError:
        pass

    return reg_key


def list_reg_keys(registry, key, architecture=None):
    """
    Returns a list of child keys as tuples containing:
        - A string that identifies the value name
        - An object that holds the value data, and whose type depends on the underlying registry type
        - An integer that identifies the type of the value data (see table in docs for _winreg.SetValueEx)
    :param registry: str, registry to look in. HKEY_LOCAL_MACHINE for example
    :param key: str, key to open 'Software/Ubisoft/Test' for example
    :param architecture: variant, int || None, 32 or 64 bit. If None, default system architecture is used
    :return: list<tuple>
    """

    import _winreg

    reg_key = get_reg_key(registry=registry, key=key, architecture=architecture)
    ret = list()
    if reg_key:
        i = 0
        while True:
            try:
                ret.append(_winreg.EnumKey(reg_key, i))
                i += 1
            except WindowsError:
                break

    return ret


def list_reg_key_values(registry, key, architecture=None):
    """
    Returns a list of child keys and their values as tuples containing:
        - A string that identifies the value name
        - An object that holds the value data, and whose type depends on the underlying registry type
        - An integer that identifies the type of the value data (see table in docs for _winreg.SetValueEx)
    :param registry: str, registry to look in. HKEY_LOCAL_MACHINE for example
    :param key: str, key to open 'Software/Ubisoft/Test' for example
    :param architecture: variant, int || None, 32 or 64 bit. If None, default system architecture is used
    :return: list<tuple>
    """

    import _winreg

    reg_key = get_reg_key(registry=registry, key=key, architecture=architecture)
    ret = list()
    if reg_key:
        sub_keys, value_count, modified = _winreg.QueryInfoKey(reg_key)
        for i in range(value_count):
            ret.append(_winreg.EnumValue(reg_key, i))

    return ret


def registry_value(registry, key, value_name, architecture=None):
    """
    Retruns the value and type of the given registry key value name
    :param registry: str, registry to look in. HKEY_LOCAL_MACHINE for example
    :param key: str, key to open 'Software/Ubisoft/Test' for example
    :param value_name: str, name of the value to read. To read the 'default' key, pass an empty string
    :param architecture: variant, int || None, 32 or 64 bit. If None, default system architecture is used
    :return: tuple<object, int, value stored in key and registry type for value (see _winreg's Value Types)
    """

    reg_key = get_reg_key(registry, key, architecture=architecture)
    if reg_key:
        import _winreg
        value = _winreg.QueryValueEx(reg_key, value_name)
        _winreg.CloseKey(reg_key)
        return value

    return '', 0
