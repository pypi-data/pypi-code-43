#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import copy
import os
from objutils.IEEE695 import Reader
from objutils import loads, dumps

BASE_DIR = r'C:\transfer\projekte\winIDEA\2009\Examples'

def recurseDirsForExtensions(base, path, result, extensions):
    curPath = os.path.join(base, *path)
    for fname in  os.listdir(curPath):
        if os.path.isdir(os.path.join(curPath, fname)):
            path.append(fname)
            recurseDirsForExtensions(base, path, result, extensions)
            path.pop(-1)
        elif os.path.isfile(os.path.join(curPath, fname)):
            _, ext = os.path.splitext(fname)
            if ext.lower() in extensions:
                print(path, fname)
                result.append((copy(path), fname))

result = []


recurseDirsForExtensions(BASE_DIR, [], result, ('.695', ))
for path, fname  in result:
    rfname = os.path.join(os.path.join(BASE_DIR, *path), fname)
    print(rfname)
    try:
        data = Reader(file(rfname))
    except Exception as e:
        print(str(e))
    else:
        print(data)
    print( "=" * 80)



def main():
    pass

if __name__=='__main__':
    main()
