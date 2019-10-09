#!/usr/bin/env python

import os
import sys
import copy
import logging
import os.path as Path

import subprocess
from mcutk.exceptions import ReadElfError

from mcutk.appbase import APPBase
from mcutk.apps import appfactory

from elftools.elf.elffile import ELFFile
from elftools.common.exceptions import ELFError
from elftools.elf.sections import SymbolTableSection
from elftools.elf.descriptions import  describe_p_flags




def transform_elf_basic(type, in_file, out_file, executor=None):
    """Transform ELF to specific type by arm-none-eabi-objcopy.

    Supported types: bin, ihex, srec.

    Arguments:
        type {str} -- which type you want to convert.
        in_file {str} -- path to elf file.
        out_file {str} -- output file
        executor {str} -- path to arm-none-eabi-objcopy, if it is None,
                    program will use the default executor(mcutk/bin/)


    Raises:
        ReadElfError -- Unknown elf format will raise such error
        Exception -- Convert failed will raise exception

    Returns:
        bool
    """
    supported = {
        'bin': "binary",
        'ihex': 'ihex',
        'srec': 'srec'
    }

    if type not in supported:
        raise ValueError("unknown type, valid choices are: %s"%(str(supported)))

    if executor is None:
        executor = Path.join(Path.dirname(__file__), 'bin/arm-none-eabi-objcopy.exe')

    try:
        with open(in_file, 'rb') as fileobj:
            elffile = ELFFile(fileobj)
            for header_name in elffile.header:
                print('{:<10s} -- {:<10s}'.format(header_name, str(elffile.header[header_name])))
    except ELFError:
        raise ReadElfError('read elf error!')

    if not os.path.isfile(executor):
        raise IOError('arm-none-eabi-objcopy does not exists!')

    type = supported.get(type, type)
    cmds = '{0} -O {1} {2} {3}'.format(executor, type, in_file, out_file)

    return subprocess.call(cmds, shell=True) == 0




def transform_elf(ide, type, in_file, out_file):
    """Transform ELF to specific type with toolchain method (app.transform_elf).

    Supported types: bin, ihex, srec.

    Arguments:
        ide {str} -- ide name or ide app instance.
        type {str} -- which type you want to convert.
        in_file {str} -- path to elf file.
        out_file {str} -- output file

    Raises:
        ReadElfError -- Unknown elf format will raise such error
        Exception -- Convert failed will raise exception

    Returns:
        bool -- success or not.
    """
    if isinstance(ide, APPBase):
        app_instance = ide
    else:
        app_instance = appfactory(ide).get_latest()

    if not (app_instance and app_instance.is_ready):
        raise ValueError('Fatal error, not found toolchain "%s" in system!'%ide)

    return app_instance.transform_elf(type, in_file, out_file)







# class ELFTool:
#     def __init__(self, elffile):
#         self.elf = elffile

#     def get_elf_symbol_by_name(self, name):
#         target_symbol = list()
#         elffile = None
#         with open(self.elf, 'rb') as f:
#             elffile = ELFFile(f)
#             for section in elffile.iter_sections():
#                 if not isinstance(section, SymbolTableSection):
#                     continue
#                 for i, sym in enumerate(section.iter_symbols()):
#                     if sym.name == name:
#                         target_symbol.append(sym)

#         for per_sym in target_symbol:
#             per_sym.entry['st_value'] = hex(per_sym.entry['st_value'])
#         return target_symbol

#     def get_elf_program_headers(self):
#         program_header = {}
#         elffile = None
#         with open(self.elf, 'rb') as f:
#             elffile = ELFFile(f)
#             program_header['entry_point'] = hex(elffile.header["e_entry"])
#             for i, segment in enumerate(elffile.iter_segments()):
#                 program_header['segment{}'.format(i)] = {
#                     'p_paddr': hex(segment['p_paddr']),
#                     'p_vaddr': hex(segment['p_vaddr']),
#                     'p_memsz': hex(segment['p_memsz']),
#                     'p_filesz': hex(segment['p_filesz']),
#                     'p_align': segment['p_align'],
#                     'p_flags': describe_p_flags(segment['p_flags'])
#                 }
#         return program_header
