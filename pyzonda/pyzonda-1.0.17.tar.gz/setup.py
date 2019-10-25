#!/usr/bin/python3

import sys
import os
from setuptools.config import read_configuration
from setuptools import setup


"""
INSTALLATION
1. Install twine package: sudo pip3 install twine 
2. Increase the number of version in setup.cfg file
3. Create new package distribution (go to the pyzonda folder): python3 setup.py sdist
5. Upload the new distribution: twine upload dist/pyzonda-[version].tar.gz
6. Uninstall old version of pyzonda: sudo -H pip3 uninstall pyzonda
7. Install last version from PyPi: sudo pip3 install -U pyzonda
8. Or install an specific version of the library: sudo pip3 install -U pyzonda=={VERSION}
"""

root_dir = os.path.abspath(os.path.dirname(__file__))
conf_dict = read_configuration(os.path.join(root_dir, 'setup.cfg'))

# Python 2.7 or later needed
if sys.version_info < (2, 7, 0, 'final', 0):
    raise SystemExit

setup()
