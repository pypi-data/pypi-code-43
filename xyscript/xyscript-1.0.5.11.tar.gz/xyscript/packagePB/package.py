#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
from xyscript.packagePB.brew_package import *
from xyscript.packagePB.pypi_package import *
from xyscript.common.xylog import warninglog,faillog

__all__ = ['pypi','brew','all']

def do():
        pass

def main():
    platform = sys.argv[1]
    
    if platform not in __all__:
        faillog("please an platform in pypi,brew and all!")
        sys.exit()
    elif platform == 'pypi':
        upload_to_pypi()
    elif platform == 'brew':
        upload_to_brew()
    elif platform == 'all':
        upload_to_pypi()
        upload_to_brew()

if __name__ == '__main__':
    main()
    