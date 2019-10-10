# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import traceback
import json


def tbprint():
    exc_traceback = sys.exc_info()[-1]
    print('Traceback:', file=sys.stderr)
    traceback.print_tb(exc_traceback, limit=1, file=sys.stderr)
    print('', file=sys.stderr)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    print('', file=sys.stderr)


def oprint(*args, **kwargs):
    print(*args, **kwargs)
    print('', **kwargs)


def opprint(*args, indent=None, **kwargs):
    for arg in args:
        print(json.dumps(arg, sort_keys=True, indent=indent, separators=(',', ': ')), **kwargs)
        print('', **kwargs)
