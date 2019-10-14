# -*- coding: utf-8 -*-
from __future__ import (print_function, unicode_literals, absolute_import)
'''
Updated 181025 - del _this_prot, not _prot
'''
import os.path as OP
from os import getcwd, environ
from importlib import import_module
from ganessa._getdll import _add_dir_to_path

# to signal dependance to _prot module for embedding tools
try:
    import ganessa._prot as _tmp
except ImportError:
    pass
else:
    del _tmp

debuglevel = 0

PKG = 'ganessa'
PATHS = ('.',
         'C:/Program Files (x86)/Safege/SafProdLicMgr',
         'C:/Program Files/Safege/SafProdLicMgr',
         'C:/Program Files/Fichiers communs/Safege',
         'C:/Program Files (x86)/Safege',
         'C:/Program Files/Safege',
         'D:/Program Files (x86)/Safege/SafProdLicMgr',
         'D:/Program Files/Safege/SafProdLicMgr',
         'D:/Program Files/Safege')
f = 'ProtDLL.dll'

def _test_import(keep=False):
    try:
        _mod = import_module('._prot', package=PKG)
    except ImportError:
        return False
    else:
        if keep:
            return _mod
        del _mod
        return True

if debuglevel > 1:
    print(' ... cwd is', getcwd())

# Recherche de la DLL par le PATH
for ndir in environ['path'].split(';'):
    if OP.exists(OP.join(ndir, f)):
        if debuglevel > 0: print(f + ' found in Path: ' + ndir)
        if _test_import(): break
        else: continue
else:
    # Puis par la liste predefinie
    for ndir in PATHS:
        if debuglevel > 1:
            print(' ... examining ' + ndir + '/' + f)
        if _add_dir_to_path(ndir, f): 
            if debuglevel > 0:
                print(' ... testing ' + ndir + '/' + f)
            if _test_import():
                if debuglevel > 0:
                    print(f + ' responding from ' + ndir)
                break
            else:
                print(f + ' found in ' + ndir + ' but *NOT* responding')
                continue
    else:
        # On n'a pas trouve
        raise ImportError('Unable to find an adequate DLL: SafProdLicMgr/' + f)

try:
    _this_prot = _test_import(keep=True)
    if not _this_prot:
        raise ImportError
except ImportError:
    print('DLL ' + f + ': not found or too old.\n')
    raise
else:
    init = _this_prot.init_prot
    config = _this_prot.config
    def close(*args):
        global _this_prot
        try:
            text = 'Protection unloaded.'
            _this_prot.close_prot()
            del _this_prot
        except NameError:
            text = 'Protection already unloaded...'
        finally:
            if args and args[0]:
                print (text)
        return text
    import atexit
    atexit.register(close)
