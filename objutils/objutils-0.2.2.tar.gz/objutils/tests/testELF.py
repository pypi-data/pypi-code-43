#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple, OrderedDict
from copy import copy
import json
import os
import sys
#import objutils.elf as Elf
#from optparse import OptionParser
#from objutils.elf import FormatError
import subprocess


BASE_DIR = r'C:\transfer\projekte\winIDEA\2009\Examples'


print(os.getcwd())


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
                #print path, fname
                result.append((copy(path), fname))

def main():
##
##    result = []
##    elfFiles = []
##    derivatives = set()
##    recurseDirsForExtensions(BASE_DIR, [], result, ('.elf'))
##    for path, fname  in result:
##        derivatives.add(path[1])
##        rfname = os.path.join(os.path.join(BASE_DIR, *path), fname)
##        if rfname.endswith('.elf'):
##            print "=" * 80
##            print rfname
##            elfFiles.append(rfname)
##            print "=" * 80
##            subprocess.call([r"C:\projekte\csProjects\yOBJl\objutils\tools\readelf.py", "-Hlt", "{0}".format(rfname)], shell = True)
##    print derivatives
##    elfFiles = {'files': elfFiles}
##    json.dump(elfFiles, open("elffiles.json", "w"))
##

# readelf -hlt /cygdrive/c/transfer/projekte/winIDEA/2009/Examples/Active/Emul1/HC12/DP256/Bank/HiWare/CPUTest.o

    #winFiles = open("/cygdrive/c/projekte/csProjects/yOBJl/objutils/winidea_files.txt").readlines()
    winFiles = open(r"C:\projekte\csProjects\yOBJl\objutils\winidea_files.txt").readlines()

    # find /cygdrive/c/transfer/projekte/winIDEA/2009/Examples/  -type f -exec file '{}' \; > idea_examples.txt
    #files = elfFiles['files']
    for line in winFiles:
        if not 'ELF' in line:
            continue
        print("=" * 80)
        fname = line.split(':')[0]
        pos = fname.index('\x00')
        fname =  fname[ : pos]
        fname = fname.replace('/cygdrive/c/', 'c:\\')
        fname = fname.replace('/', '\\')
        print(fname)
        print("=" * 80)
        sys.stdout.flush()
        #subprocess.call([r"/cygdrive/c/projekte/csProjects/yOBJl/objutils/tools/readelf.py", "-Hlt", '"{0}"'.format(fname)], shell = True)
        subprocess.call([r"C:\projekte\csProjects\yOBJl\objutils\tools\readelf.py", "-Hlt", "{0}".format(fname),">","df.0"], shell = True)
        subprocess.call([r"readelf", "-hlt", "{0}".format(fname),">","df.1"], shell = True)
        subprocess.call(["diff", "-aw -U 1", "df.0", "df.1"], shell = True)
        #sys.exit(1)
        sys.stdout.flush()

if __name__ == '__main__':
    main()

# find C:\transfer\projekte\winIDEA\2009\Examples -type f | xargs file -

"""

$ readelf -hltsg --debug-dump /cygdrive/c/transfer/projekte/winIDEA/2009/Examples/Active/Emul2/Coolrisc/Debug/sample.o

readelf: Error: Missing knowledge of 32-bit reloc types used in DWARF sections of machine number 51222
Aborted (Speicherabzug geschrieben)

"""
