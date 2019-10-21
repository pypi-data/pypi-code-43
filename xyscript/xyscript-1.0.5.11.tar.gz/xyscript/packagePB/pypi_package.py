#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
from xyscript.common.xylog import *
from xyscript.config import Condig

def upload_to_pypi():
    print("upload_to_pypi")
    try:
        
        package_wheel_shell = 'python setup.py sdist bdist_wheel'
        version = Config().get_version()
        upload_shell = 'twine upload dist/xyscript-' + version + '.tar.gz'
        printandresult(package_wheel_shell)
        text = printandresult(upload_shell)
        successlog('package to pypi success!')
    except BaseException as error:
        faillog('package to pypi failed!')

def main():
    pass

if __name__ == '__main__':
    main()
    
    