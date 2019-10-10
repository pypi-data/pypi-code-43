#!/usr/bin/python

from ctypes import cdll, c_int, c_char_p, create_string_buffer, c_ulonglong
from sys import platform
from os import path

class crcLib(object):
    def __init__(self):
        self.library = None
        self.lib_file = None

    def load(self, lib_dir):
        if platform == 'darwin':
            self.lib_file = 'libcrclib.dylib'
        elif platform == 'linux':
            self.lib_file = 'libcrclib.so'
        elif platform == 'win32':
            self.lib_file = 'libcrclib.dll'

        libpath = path.join(lib_dir, self.lib_file)
        try:
            self.library = cdll.LoadLibrary(libpath)
        except OSError as err:
            print('OSError', err)

    def crc32sum(self, buffer, buffer_sz) -> c_ulonglong:
        func = self.library.calcCrc
        func.restype = c_ulonglong
        func.argtypes = [
            c_char_p, # unsigned char* buffer
            c_int,    # size_t buffer_sz
        ]
        data = create_string_buffer(buffer_sz)
        data.value = buffer
        result = func(data, buffer_sz)

        return result
