#!/usr/bin/env python
import sys
from xdis import load_module
pyc_file = sys.argv[1]
(version, timestamp, magic_int, co, is_pypy,
 source_size) = load_module(pyc_file)
print(type(co))
exec(co)
