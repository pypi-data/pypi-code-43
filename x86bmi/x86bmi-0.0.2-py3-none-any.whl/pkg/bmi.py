
import sys
import numpy as np
from ctypes import *

#if sys.platform.startswith('darwin'):
  #_extname = 'dylib'
#elif sys.platform.startswith('linux'):
  #_extname = 'so'
#else: # assume windows
  #_extname = '.dll'
_extname = 'so'
_lib = CDLL('./bmi_intrin.' + _extname)

def __call1_1(fname, x):
  s = x.itemsize
  if s < 4:
    x = x.astype(x.dtype.str[:2] + '4')
    s = 4
  f = getattr(_lib, fname + str(s * 8)) # the function ptr is cached
  y = np.empty(x.shape, np.dtype('<u' + str(s)))
  f(x.ctypes.data_as(c_void_p), y.ctypes.data_as(c_void_p), x.size)
  return y

def __call2_1(fname, x, y):
  s = x.itemsize
  if s < 4:
    x = x.astype(x.dtype.str[:2] + '4')
    y = y.astype(y.dtype.str[:2] + '4')
    s = 4
  f = getattr(_lib, fname + str(s * 8)) # the function ptr is cached
  z = np.empty(x.shape, np.dtype('<u' + str(s)))
  f(x.ctypes.data_as(c_void_p), y.ctypes.data_as(c_void_p), z.ctypes.data_as(c_void_p), x.size)
  return z

def popcnt(x):
  return __call1_1('popcnt', x)
def lzcnt(x):
  return __call1_1('lzcnt', x)
def tzcnt(x):
  return __call1_1('tzcnt', x)
def blsi(x):
  return __call1_1('blsi', x)
def blsmsk(x):
  return __call1_1('blsmsk', x)
def blsr(x):
  return __call1_1('blsr', x)

def msbpos(x):
  s = x.dtype.type(x.itemsize*8)
  s = np.maximum(32, s)
  return s - lzcnt(x)

def bzhi(x, y):
  return __call2_1('bzhi', x, y)
def pdep(x, y):
  return __call2_1('pdep', x, y)
def pext(x, y):
  return __call2_1('pext', x, y)
