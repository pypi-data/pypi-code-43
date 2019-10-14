#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2019, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------

from setuptools import setup, find_packages
import os
import sys
import versioneer

# pull in some definitions from the package's __init__.py file
basedir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(basedir, 'src', ))
import stdlogpj as package


verbose=1
with open(os.path.join(basedir, 'README.md'), 'r') as fp:
    long_description = fp.read()


setup (
    name             = package.__package_name__,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(),
    license          = package.__license__,
    description      = package.__description__,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author           = package.__author_name__,
    author_email     = package.__author_email__,
    url              = package.__url__,
    #download_url=package.__download_url__,
    keywords         = package.__keywords__,
    platforms        = 'any',
    install_requires = package.__install_requires__,
    package_dir      = {
        '': 'src', 
        package.__package_name__: 'src/'+package.__package_name__
        },
    # packages         = find_packages(),
    packages         = [package.__package_name__, ],
    package_data     = {
         package.__package_name__: [
            'LICENSE.txt',
            ],
         },
    classifiers      = package.__classifiers__,
    entry_points     = {
         # create & install scripts in <python>/bin
         # 'console_scripts': [],
         #'gui_scripts': [],
    },
    zip_safe         = package.__zip_safe__,
    python_requires  = package.__python_version_required__,
)
