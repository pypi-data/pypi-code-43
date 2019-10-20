#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"

__copyright__ = """
    objutils - Object file library for Python.

   (C) 2010-2017 by Christoph Schueler <cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from collections import namedtuple
import enum
import mmap
import os
from pprint import pprint
import sys
import time
import types
import struct

import construct
from construct import Struct, If, Const, Adapter, FlagsEnum, Enum, String, Array, Padding, HexDump, Tell, Union
from construct import Probe, CString, IfThenElse, Pass, Float64l, Int8ul, Construct, this, GreedyBytes, Switch
from construct import Pointer, Byte, GreedyRange, Bytes, Int16ul, Int16sl, Int32ul, Int64ul
import six

from objutils.utils import create_memorymapped_fileview, slicer

DOS_MAGIC = b'MZ'
PE_MAGIC = b"PE\x00\x00"

#define IMAGE_DOS_SIGNATURE                 0x5A4D      // MZ
#define IMAGE_OS2_SIGNATURE                 0x454E      // NE
#define IMAGE_OS2_SIGNATURE_LE              0x454C      // LE
#define IMAGE_VXD_SIGNATURE                 0x454C      // LE
#define IMAGE_NT_SIGNATURE                  0x00004550  // PE00


class PrintContext(Construct):

    def _parse(self, stream, context):
        print(context)

class DateTimeAdapter(Adapter):

    def _decode(self, obj, context):
        return time.ctime(obj)


class DirectoryEntry(enum.IntEnum):

    EXPORT          = 0   # Export Directory
    IMPORT          = 1   # Import Directory
    RESOURCE        = 2   # Resource Directory
    EXCEPTION       = 3   # Exception Directory
    SECURITY        = 4   # Security Directory
    BASERELOC       = 5   # Base Relocation Table
    DEBUG           = 6   # Debug Directory
#    _COPYRIGHT       7   // (X86 usage)
    ARCHITECTURE    = 7   # Architecture Specific Data
    GLOBALPTR       = 8   # RVA of GP
    TLS             = 9   # TLS Directory
    LOAD_CONFIG     = 10  # Load Configuration Directory
    BOUND_IMPORT    = 11  # Bound Import Directory in headers
    IAT             = 12  # Import Address Table
    DELAY_IMPORT    = 13  # Delay Load Import Descriptors
    COM_DESCRIPTOR  = 14  # COM Runtime descriptor



##
## File header format.
##
DOSFileHeader = "DOSFileHeader" / Struct(
    Const(DOS_MAGIC),
    "e_cblp" / Int16ul,
    "e_cp" / Int16ul,
    "e_crlc" / Int16ul,
    "e_cparhdr" / Int16ul,
    "e_minalloc" / Int16ul,
    "e_maxalloc" / Int16ul,
    "e_ss" / Int16ul,
    "e_sp" / Int16ul,
    "e_csum" / Int16ul,
    "e_ip" / Int16ul,
    "e_cs" / Int16ul,
    "e_lfarlc" / Int16ul,
    "e_ovno" / Int16ul,
    "e_res" / Int16ul,
    Padding(3 * 2),
    "e_oemid" / Int16ul,
    "e_oeminfo" / Int16ul,
    "e_res2" / Int16ul,
    Padding(9 * 2),
    "e_lfanew" / Int32ul,
#    Int16ul("e_"),
)


PEFileHeader = "PEFileHeader" / Struct(
    Const(PE_MAGIC),
    "Machine" / Enum(Int16ul,
        MACHINE_UNKNOWN           = 0,
        MACHINE_I386              = 0x014c,  # Intel 386.
        MACHINE_R3000             = 0x0162,  # MIPS little-endian, 0x160 big-endian
        MACHINE_R4000             = 0x0166,  # MIPS little-endian
        MACHINE_R10000            = 0x0168,  # MIPS little-endian
        MACHINE_WCEMIPSV2         = 0x0169,  # MIPS little-endian WCE v2
        MACHINE_ALPHA             = 0x0184,  # Alpha_AXP
        MACHINE_SH3               = 0x01a2,  # SH3 little-endian
        MACHINE_SH3DSP            = 0x01a3,
        MACHINE_SH3E              = 0x01a4,  # SH3E little-endian
        MACHINE_SH4               = 0x01a6,  # SH4 little-endian
        MACHINE_SH5               = 0x01a8,  # SH5
        MACHINE_ARM               = 0x01c0,  # ARM Little-Endian
        MACHINE_THUMB             = 0x01c2,
        MACHINE_AM33              = 0x01d3,
        MACHINE_POWERPC           = 0x01F0,  # IBM PowerPC Little-Endian
        MACHINE_POWERPCFP         = 0x01f1,
        MACHINE_IA64              = 0x0200,  # Intel 64
        MACHINE_MIPS16            = 0x0266,  # MIPS
        MACHINE_ALPHA64           = 0x0284,  # ALPHA64
        MACHINE_MIPSFPU           = 0x0366,  # MIPS
        MACHINE_MIPSFPU16         = 0x0466,  # MIPS
        # MACHINE_AXP64             = MACHINE_ALPHA64,
        MACHINE_TRICORE           = 0x0520,  # Infineon
        MACHINE_CEF               = 0x0CEF,
        MACHINE_EBC               = 0x0EBC,  # EFI Byte Code
        MACHINE_AMD64             = 0x8664,  # AMD64 (K8)
        MACHINE_M32R              = 0x9041,  # M32R little-endian
        MACHINE_CEE               = 0xC0EE,
        _default_dict             = Pass,
    ),
    "NumberOfSections" / Int16ul,
    "TimeDateStamp" / DateTimeAdapter(Int32ul),
    "PointerToSymbolTable" / Int32ul,
    "NumberOfSymbols" / Int32ul,
    "SizeOfOptionalHeader" / Int16ul,

#    "Symbols" / If(this.NumberOfSymbols != 0, Pointer(this.PointerToSymbolTable,
#        Array(lambda ctx: ctx.NumberOfSymbols,
#              "Symbol" / Struct (
#                  "Name" / String(8, encoding = "utf8"),
#                  "Value" / Int32ul,
#                  "SectionNumber" / Int16ul,
#                  "Type" / Int16ul,
#                  "StorageClass" / Int8ul,
#                  "NumberOfAuxSymbols" / Int8ul,
#              )
#        )
#    )),

    "Characteristics" / FlagsEnum(Int16ul,
        RELOCS_STRIPPED           = 0x0001,  # Relocation info stripped from file.
        EXECUTABLE_IMAGE          = 0x0002,  # File is executable  (i.e. no unresolved externel references).
        LINE_NUMS_STRIPPED        = 0x0004,  # Line nunbers stripped from file.
        LOCAL_SYMS_STRIPPED       = 0x0008,  # Local symbols stripped from file.
        AGGRESIVE_WS_TRIM         = 0x0010,  # Agressively trim working set
        LARGE_ADDRESS_AWARE       = 0x0020,  # App can handle >2gb addresses
        BYTES_REVERSED_LO         = 0x0080,  # Bytes of machine word are reversed.
        MACHINE_32BIT             = 0x0100,  # 32 bit word machine.
        DEBUG_STRIPPED            = 0x0200,  # Debugging info stripped from file in .DBG file
        REMOVABLE_RUN_FROM_SWAP   = 0x0400,  # If Image is on removable media, copy and run from the swap file.
        NET_RUN_FROM_SWAP         = 0x0800,  # If Image is on Net, copy and run from the swap file.
        SYSTEM                    = 0x1000,  # System File.
        DLL                       = 0x2000,  # File is a DLL.
        UP_SYSTEM_ONLY            = 0x4000,  # File should only be run on a UP machine
        BYTES_REVERSED_HI         = 0x8000,  # Bytes of machine word are reversed.
    ),
    "OptionalHeader" / If (this.SizeOfOptionalHeader > 0,
       Struct(
            "Magic" / Enum(Int16ul,
                PE = 0x010b,
                PEPlus = 0x020b
            ),

            #
            # COFF Standard-Headers (including Unix).
            #
            "MajorLinkerVersion" / Int8ul,
            "MinorLinkerVersion"/ Int8ul,
            "SizeOfCode" / Int32ul,
            "SizeOfInitializedData" / Int32ul,
            "SizeOfUninitializedData" / Int32ul,
            "AddressOfEntryPoint" / Int32ul,
            "BaseOfCode" / Int32ul,

            "BaseOfData" / If (this.Magic == "PE",
                Int32ul,
            ),
            #
            # NT Additional Fields.
            #
            "ImageBase" /  IfThenElse(this.Magic == "PEPlus",
                Int64ul,
                Int32ul,
            ),

            "SectionAlignment" / Int32ul,
            "FileAlignment" / Int32ul,

            "MajorOperatingSystemVersion" / Int16ul,
            "MinorOperatingSystemVersion" / Int16ul,
            "MajorImageVersion" / Int16ul,
            "MinorImageVersion" / Int16ul,
            "MajorSubsystemVersion" / Int16ul,
            "MinorSubsystemVersion" / Int16ul,

            "Win32VersionValue" / Int32ul,
            "SizeOfImage" / Int32ul,
            "SizeOfHeaders" / Int32ul,
            "CheckSum" / Int32ul,

            "Subsystem" / Enum(Int16ul,
                IMAGE_SUBSYSTEM_UNKNOWN = 0,
                IMAGE_SUBSYSTEM_NATIVE = 1,
                IMAGE_SUBSYSTEM_WINDOWS_GUI = 2,
                IMAGE_SUBSYSTEM_WINDOWS_CUI = 3,
                IMAGE_SUBSYSTEM_POSIX_CUI = 7,
                IMAGE_SUBSYSTEM_WINDOWS_CE_GUI = 9,
                IMAGE_SUBSYSTEM_EFI_APPLICATION = 10,
                IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER = 11,
                IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER = 12,
                IMAGE_SUBSYSTEM_EFI_ROM = 13,
                IMAGE_SUBSYSTEM_XBOX = 14,
            ),

            "DllCharacteristics" / Int16ul,

            "SizeOfStackReserve" / IfThenElse(this.Magic == "PEPlus",
                Int64ul,
                Int32ul,
            ),
            "SizeOfStackCommit" / IfThenElse(this.Magic == "PEPlus",
                Int64ul,
                Int32ul,
            ),
            "SizeOfHeapReserve" / IfThenElse(this.Magic == "PEPlus",
                Int64ul,
                Int32ul,
            ),
            "SizeOfHeapCommit" / IfThenElse(this.Magic == "PEPlus",
                Int64ul,
                Int32ul,
            ),
            "LoaderFlags" / Int32ul,
            "NumberOfRvaAndSizes" / Int32ul,

            "Directory" / Array(lambda ctx: ctx.NumberOfRvaAndSizes,
                "Entry" / Struct(
                    "VirtualAddress" / Int32ul,
                    "Size" / Int32ul,
                ),
            ),
        ),
    ),
    "end" / Tell,
)


Section = "Section" / Struct (
    "Name" / String(8, encoding="utf8"),
    "VirtualSize" / Int32ul,
    "VirtualAddress" / Int32ul,
    "SizeOfRawData" / Int32ul,
    "PointerToRawData" / Int32ul,

    #"data"/If (this.SizeOfRawData != 0, OnDemandPointer(this.PointerToRawData, Bytes(8))),
    #"data" / If (this.SizeOfRawData != 0, Bytes(8)),

    #"PointerToRawData" / Bytes(4),
    "PointerToRelocations" / Int32ul,
    "PointerToLinenumbers" / Int32ul,
    "NumberOfRelocations" / Int16ul,
    "NumberOfLinenumbers" / Int16ul,
    "Characteristics" / FlagsEnum(Int32ul,
        IMAGE_SCN_TYPE_NO_PAD = 0x00000008,
        IMAGE_SCN_CNT_CODE = 0x00000020,
        IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040,
        IMAGE_SCN_CNT_UNINITIALIZED_DATA = 0x00000080,
        IMAGE_SCN_LNK_OTHER = 0x00000100,
        IMAGE_SCN_LNK_INFO = 0x00000200,
        IMAGE_SCN_LNK_REMOVE = 0x00000800,
        IMAGE_SCN_LNK_COMDAT = 0x00001000,
        IMAGE_SCN_GPREL = 0x00008000,
        IMAGE_SCN_MEM_PURGEABLE = 0x00020000,
        IMAGE_SCN_MEM_16BIT = 0x00020000,
        IMAGE_SCN_MEM_LOCKED = 0x00040000,
        IMAGE_SCN_MEM_PRELOAD = 0x00080000,
        IMAGE_SCN_ALIGN_1BYTES = 0x00100000,
        IMAGE_SCN_ALIGN_2BYTES = 0x00200000,
        IMAGE_SCN_ALIGN_4BYTES = 0x00300000,
        IMAGE_SCN_ALIGN_8BYTES = 0x00400000,
        IMAGE_SCN_ALIGN_16BYTES = 0x00500000,
        IMAGE_SCN_ALIGN_32BYTES = 0x00600000,
        IMAGE_SCN_ALIGN_64BYTES = 0x00700000,
        IMAGE_SCN_ALIGN_128BYTES = 0x00800000,
        IMAGE_SCN_ALIGN_256BYTES = 0x00900000,
        IMAGE_SCN_ALIGN_512BYTES = 0x00A00000,
        IMAGE_SCN_ALIGN_1024BYTES = 0x00B00000,
        IMAGE_SCN_ALIGN_2048BYTES = 0x00C00000,
        IMAGE_SCN_ALIGN_4096BYTES = 0x00D00000,
        IMAGE_SCN_ALIGN_8192BYTES = 0x00E00000,
        IMAGE_SCN_LNK_NRELOC_OVFL = 0x01000000,
        IMAGE_SCN_MEM_DISCARDABLE = 0x02000000,
        IMAGE_SCN_MEM_NOT_CACHED = 0x04000000,
        IMAGE_SCN_MEM_NOT_PAGED = 0x08000000,
        IMAGE_SCN_MEM_SHARED = 0x10000000,
        IMAGE_SCN_MEM_EXECUTE = 0x20000000,
        IMAGE_SCN_MEM_READ = 0x40000000,
        IMAGE_SCN_MEM_WRITE = 0x80000000,
    )
)

# www.osdever.net/documents/PECOFF.pdf

Symbol = "Symbol" / Struct (
#    "Name" / String(8, encoding = "utf8"),
    "Name" / Bytes(8),
    "Value" / Int32ul,
    "SectionNumber" / Int16ul,
    "Type" / Int16ul,
    "StorageClass" / Int8ul,
    "NumberOfAuxSymbols" / Int8ul,
)

SYMBOL_SIZE = 18

import itertools
import sys


if len(sys.argv) > 1:
    TEST_FILE = sys.argv[1]
else:
    TEST_FILE = r'C:\projekte\csProjects\k-ps\tests\Posix_Serial.exe'
#TEST_FILE = r'C:\projekte\csProjects\k-ps\tools\libzmq-v120-mt-4_0_4.dll'
    TEST_FILE = r'C:\projekte\csProjects\yOBJl\objutils\tests\win\main.exe'
    TEST_FILE ='c:/projekte/diverse/win2k/private/inet/mshtml/tools/alpha/bin/c1.exe'


def getSlice(fp, offset, elemSize, numElems):
    return fp[offset : offset + (numElems * elemSize)]

def toSymbol(data):
    res =  Symbol.parse(data)
    return res, data

def parserFactory(constructType):
    return constructType(encoding="utf8").parse

parseCString = parserFactory(CString)

def buildSymbols(rawSymbols, stringTable):
    result = []
    symbolIter = itertools.chain(rawSymbols)
    for idx, (symbol, raw) in enumerate(symbolIter):
        print("Idx: {}".format(idx))
        if symbol.Name.startswith(b'\x00\x00\x00\x00'):
            value = struct.unpack("<I", symbol.Name[ 4 : ])[0]
            nameValue = parseCString(stringTable[value : ])
            print("NameValue: ", nameValue)
        if symbol.NumberOfAuxSymbols:
            #if symbol.Name
            aux = [next(symbolIter) for _ in range(symbol.NumberOfAuxSymbols)]
            if symbol.StorageClass == 103:
                #sname = CString().parse(symbol.Name)
                sname = parseCString(symbol.Name)
                assert(sname == b'.file')
                #fileName = CString(8, encoding="utf8").parse(aux[0][1])
                rawValue = aux[0][1]
                if six.PY3:
                    rawValue = rawValue.tobytes()
                term = rawValue.find(b'\x00')
                if term == -1:
                    fileName = rawValue
                else:
                    fileName = rawValue[ : term]
                if six.PY3:
                    #fileName = fileName.tobytes()
                    pass
                print("Auxiliary Format 4: {}".format(fileName))
        elif symbol.StorageClass == 101:
            filName = ""
            print("Auxiliary Format 2 (Funktion): {}".format(fileName))

            #print(symbol, aux)
    return result

def main():
    peFile =  create_memorymapped_fileview(TEST_FILE)
    dosHeader = DOSFileHeader.parse(peFile[ : DOSFileHeader.sizeof()])
    print(dosHeader)

    pe0 = PEFileHeader.parse(peFile[ dosHeader.e_lfanew : ])
    print(pe0)
    syms = getSlice(peFile, pe0.PointerToSymbolTable, SYMBOL_SIZE, pe0.NumberOfSymbols)

    if pe0.NumberOfSymbols:
        stringtableOffset = pe0.PointerToSymbolTable + (SYMBOL_SIZE * pe0.NumberOfSymbols)
        stLen = struct.unpack("<I", peFile[stringtableOffset : stringtableOffset + 4])[0]
        stringTable = peFile[stringtableOffset : stringtableOffset + stLen + 1]
        #print("STRINGS: ", stLen, stringTable.tobytes())
    else:
        stringTable = None

    rawSymbols = slicer(syms, SYMBOL_SIZE, toSymbol)
    #print(rawSymbols, len(rawSymbols), pe0.NumberOfSymbols)
    symbols = buildSymbols(rawSymbols, stringTable)

    # // Ignoring typecasts and pointer conversion issues for clarity...
    #  pNTHeader = dosHeader + dosHeader->e_lfanew;


    sectionData = getSlice(peFile, dosHeader.e_lfanew + pe0.end, Section.sizeof(), pe0.NumberOfSections)

    pos = 0
    for idx in range(pe0.NumberOfSections):
        section = Section.parse(sectionData[ pos : pos + Section.sizeof()])
        if section.Name.startswith("/") and stringTable:
            section.Name = parseCString(stringTable[int(section.Name[1:]) : ])
        pos += Section.sizeof()
        print(section)
        if section.SizeOfRawData != 0:
            # If SizeOfRawData is less than VirtualSize, the remainder is padded with zeros.
            print("PTR: ", section.PointerToRawData)
            sdata = peFile[section.PointerToRawData : section.PointerToRawData + section.SizeOfRawData]
            #print("CHUNK: ", sdata.tobytes())


if __name__ == '__main__':
    main()


##
## Microsoft Portable Executable and Common Object File Format
## s. http://www.microsoft.com/whdc/system/platform/firmware/PECOFF.mspx
##    WinNT.h
##

MSDOS_SIGNATURE     = 0x5a4d        # 'MZ'
PE_SIGNATURE        = 0x00004550    # 'PE00'
OS2_SIGNATURE       = 0x454E        # 'NE'
OS2_SIGNATURE_LE    = 0x454C        # 'LE'
VXD_SIGNATURE_LE    = 0x454C        # 'LE'
PE_OFFSET           = 0x3c


NUMBEROF_DIRECTORY_ENTRIES    = 16

"""
class OptionalHeader(Structure):
    ##
    ## Standard fields.
    ##
    magic                       = Word(1)
    majorLinkerVersion          = Byte(2)
    minorLinkerVersion          = Byte(3)
    sizeOfCode                  = DWord(4)
    sizeOfInitializedData       = DWord(5)
    sizeOfUninitializedData     = DWord(6)
    addressOfEntryPoint         = DWord(7)
    baseOfCod                   = DWord(8)
    baseOfData                  = DWord(9)
    ##
    ## NT additional fields.
    ##
    imageBase                   = DWord(10)
    sectionAlignment            = DWord(11)
    fileAlignment               = DWord(12)
    majorOperatingSystemVersion = Word(13)
    minorOperatingSystemVersion = Word(14)
    majorImageVersion           = Word(15)
    minorImageVersion           = Word(16)
    majorSubsystemVersion       = Word(17)
    minorSubsystemVersion       = Word(18)
    win32VersionValue           = DWord(19)
    sizeOfImage                 = DWord(20)
    sizeOfHeaders               = DWord(21)
    checkSum                    = DWord(22)
    subsystem                   = Word(23)
    dllCharacteristics          = Word(24)
    sizeOfStackReserve          = DWord(25)
    sizeOfStackCommit           = DWord(26)
    sizeOfHeapReserve           = DWord(27)
    sizeOfHeapCommit            = DWord(28)
    loaderFlags                 = DWord(29)
    numberOfRvaAndSizes         = DWord(30)
#    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
    dataDirectory               = DataDirectory(31, NUMBEROF_DIRECTORY_ENTRIES)
"""

