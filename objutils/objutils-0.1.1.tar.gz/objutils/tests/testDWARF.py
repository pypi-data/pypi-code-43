#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple, OrderedDict
from copy import copy
import os
from pprint import pprint
import objutils.elf as Elf
from optparse import OptionParser
from objutils.dwarf import die, constants, DebugSectionReader
from objutils.elf import FormatError

"""
The ELF sections and their contents are
========================================================================
    .debug_abbrev       Abbreviations used in the .debug_info  section
    .debug_aranges      A mapping between memory address and compilation 
    .debug_frame        Call Frame Information 
    .debug_info         The core DWARF data containing DIEs 
    .debug_line         Line Number Program 
    .debug_loc          Location descriptions
    .debug_macinfo      Macro descriptions 
    .debug_pubnames     A lookup table for global objects and functions 
    .debug_pubtypes     A lookup table for global types
    .debug_ranges       Address ranges referenced by DIEs 
    .debug_str          String table used by .debug_info
    .debug_types        Type descriptions
"""

POS = r"C:\transfer\projekte\winIDEA\2009\Examples\ActivePRO\S12X\MC9S12XDP512\Metrowerks\Debug\sample.elf"    # POSITIV-BEISPIEL.

FILE_NAME = r'C:\projekte\csProjects\yOBJl\tests\C2B_12.elf'
#FILE_NAME = r'C:\projekte\csProjects\yOBJl\tests\cygmon.elf'
#FILE_NAME = r'C:\projekte\pyInst\pyelftools-0.21\examples\sample_exe64.elf'
FILE_NAME = r'C:\transfer\projekte\winIDEA\2009\Examples\iTRACE_PRO\ARM7\EVB\ST30\DataProfiler\Debug\sample.elf'
FILE_NAME = r'C:\transfer\projekte\winIDEA\2009\Examples\AsystTrace\Examples\ITMPC5554\Debug\sample.elf'

FILE_NAME = 'C:\transfer\projekte\winIDEA\2009\Examples\AsystTrace\Examples\ITLPC2138\Debug\sample.elf' # Gleich mehrere Fehler!!!

BASE_DIR = r'C:\transfer\projekte\winIDEA\2009\Examples'

STOP_LIST = ['C:\transfer\projekte\winIDEA\2009\Examples\OnChip\MAC7x00\MAC7100\GHS\Debug\sample.elf']

print(os.getcwd())

DebugInfo = namedtuple('DebugInfo', 'section, image')

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

def dumpDWARF(elf):
    debugSections = OrderedDict()
    for section in elf.sectionHeaders:
        name = elf.getString(section.parent.header.elfStringTableIndex, section.shNameIdx)
        print(name)
        if name.startswith('.debug'):
            if name == '.debug_abbrev':
                pass
            debugSections[name] = section
    result = OrderedDict()
    for name, section in debugSections.items():
        image = section.image
        result[name]= DebugInfo(section, image)
    return result

def main():
    usage = "usage: %prog [options] elf_file"

    result = []
    derivatives = set()
    recurseDirsForExtensions(BASE_DIR, [], result, ('.elf', '.695', '.map'))
    for path, fname  in result:
        derivatives.add(path[1])
        rfname = os.path.join(os.path.join(BASE_DIR, *path), fname)
        if rfname in STOP_LIST:
            continue
        print("=" * 80)
        print(rfname)
        print("=" * 80)
        if rfname.endswith('.elf'):
            try:
                reader = Elf.Reader(rfname)
                dbgData = dumpDWARF(reader)
                dr = DebugSectionReader(dbgData, reader.byte_order_prefix)
                res = dr.process()
            except (OverflowError, FormatError) as e:  # AttributeError
                print("*** EXCEPTION: [%s] ***" % e)
            except Exception as e:
                print("*** EXCEPTION: [%s] ***" % e)
                raise
    print(derivatives)
    #outf = open("debug_abbrev.bin", "wb")
    #print >> outf, dbgData['.debug_abbrev'].image
    #outf.close()

#POS = r"C:\transfer\projekte\winIDEA\2009\Examples\ActivePRO\TMS470\TMS470R1V8x SE4\Debug\sample.elf"
#POS = r"C:\transfer\projekte\winIDEA\2009\Examples\ActivePRO\TMS470\TMS470Pxx Standard\Debug\sample.elf"
POS = r'C:\transfer\projekte\winIDEA\2009\Examples\iTRACE_GT\MPC55xx\ITMPC5554\GCC\Traffic Lights\Debug\sample.elf'
#POS = r'C:\transfer\projekte\winIDEA\2009\Examples\OnChip\MAC7x00\MAC7100\GHS\Debug\sample.elf'
#POS = r'C:\transfer\projekte\winIDEA\2009\Examples\OnChip\PowerPC\MPC55xx\ITMPC5554\DiabData\Debug\sample.elf'
POS = r'C:\transfer\projekte\winIDEA\2009\Examples\OnChip\XC16x_XC2xxx\EvaBoard\InfineonXC2287\Tasking\Debug\Sample.elf'

POS = r'C:\projekte\csProjects\yOBJl\objutils\tests\ELFFiles\testfile51'

if __name__ == '__main__':
    reader = Elf.Reader(POS)
    dbgData = dumpDWARF(reader)
    dr = DebugSectionReader(dbgData, reader.byte_order_prefix)
    res = dr.process()
    pprint(dr.abbrevs)
#   main()

# objutils is a versatile ??? libarary, especially targetted to embedded systems (guys|folks).

