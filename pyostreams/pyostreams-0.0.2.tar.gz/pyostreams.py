#!/usr/bin/env python
from ctypes import CDLL, c_char_p, c_int, c_void_p, c_ulonglong
from os import read, write
from time import sleep
import eventlet
# import gevent
# from gevent.socket import wait_read

_lib = CDLL('libciostreams.so')
_lib.factory_make.restype = c_void_p
_lib.factory_make.argtypes = (c_char_p,)

_lib.upload_prepare.restype = c_int
_lib.upload_prepare.argtypes = (c_void_p, c_char_p)

_lib.upload_write_single.restype = c_int
_lib.upload_write_single.argtypes = (c_void_p, c_void_p, c_int)

_lib.upload_commit.restype = c_int
_lib.upload_commit.argtypes = (c_void_p,)

_lib.upload_abort.restype = c_int
_lib.upload_abort.argtypes = (c_void_p,)

_lib.get_fd.restype = c_int
_lib.get_fd.argtypes = (c_void_p,)

_lib.get_len.restype = c_int
_lib.get_len.argtypes = (c_void_p,)

class BackgroundTask:
    def __init__(self):
        pass
    def make(self, hello):
        self.ctx = _lib.factory_make(hello)
        self.fd = _lib.get_fd(self.ctx)
        self.ret = 0
        pass
    def prepare(self, targets):
        return _lib.upload_prepare(self.ctx, targets)
        pass
    def write_single(self, content, size):
        if self.ret:
            return self.ret
        eventlet.hubs.trampoline(self.fd, read=True)
        read(self.fd, 8)
        self.ret = _lib.upload_write_single(self.ctx, content, size)
        return self.ret 
        pass
    def commit(self):
        return _lib.upload_commit(self.ctx)
        pass
    def __del__(self):
        pass
