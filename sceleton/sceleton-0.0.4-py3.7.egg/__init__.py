import sys

if sys.version_info < (3, 5):
  raise AssertionError('The required version of python is >= 3.5')
