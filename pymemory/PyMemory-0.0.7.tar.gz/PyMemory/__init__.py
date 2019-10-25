from ctypes import CDLL
import os


class PyMemory:
    def __init__(self, window_title, file_name):
        self.PyMemoryDll = CDLL(os.path.abspath(__file__).replace("__init__.py", "PyMemory.dll"))
        self.window_title = window_title
        self.file_name = file_name
        self.window_hwnd = self.PyMemoryDll.GetHWND(window_title)
        self.process_pid = self.PyMemoryDll.GetProcessIDbyName(file_name)
        self.window_pid = self.PyMemoryDll.GetWindowThreadPID(self.window_hwnd, self.process_pid)
        self.window_process_hwnd = None

    def OpenProcess(self):
        self.window_process_hwnd = self.PyMemoryDll.OpenProc(self.window_pid)

    def CloseProcess(self):
        self.PyMemoryDll.CloseProc(self.window_process_hwnd)

    def ReadProcessMemory(self, maddress):
        self.OpenProcess()
        ReadData = self.PyMemoryDll.Read(self.window_process_hwnd, maddress)
        self.CloseProcess()
        return ReadData

