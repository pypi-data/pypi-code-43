from builtins import object

import platform

_is_windows = "Windows" in platform.system()

ERROR_INVALID_PARAMETER = 0x0057
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

if _is_windows:
    import os
    import msvcrt
    import ctypes

    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    def _check_bool(result, func, args):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return args

    LPDWORD = ctypes.POINTER(wintypes.DWORD)
    kernel32.GetConsoleMode.errcheck = _check_bool
    kernel32.GetConsoleMode.argtypes = (wintypes.HANDLE, LPDWORD)
    kernel32.SetConsoleMode.errcheck = _check_bool
    kernel32.SetConsoleMode.argtypes = (wintypes.HANDLE, wintypes.DWORD)


class Win10Mixin(object):
    def __init__(self):
        self.supported_attrs = []
        self.old_mode = None

    def setup(self, appstate):
        global _is_windows
        if not _is_windows:
            return

        # don't assume StandardOutput is a console.
        # open CONOUT$ instead
        fdout = os.open("CONOUT$", os.O_RDWR)
        try:
            hout = msvcrt.get_osfhandle(fdout)
            self.old_mode = wintypes.DWORD()
            kernel32.GetConsoleMode(hout, ctypes.byref(self.old_mode))
            mode = self.old_mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(hout, mode)
        except OSError as e:
            self._handle_oserror(e)
            raise e
        finally:
            os.close(fdout)

    def teardown(self, appstate):
        global _is_windows
        if not _is_windows:
            return

        # don't assume StandardOutput is a console.
        # open CONOUT$ instead
        fdout = os.open("CONOUT$", os.O_RDWR)
        try:
            hout = msvcrt.get_osfhandle(fdout)
            kernel32.SetConsoleMode(hout, self.old_mode)
        except OSError as e:
            self._handle_oserror(e)
            raise e
        finally:
            os.close(fdout)

    def _handle_oserror(self, e):
        try:
            if e.winerror == ERROR_INVALID_PARAMETER:
                raise NotImplementedError
        except Exception:
            return
