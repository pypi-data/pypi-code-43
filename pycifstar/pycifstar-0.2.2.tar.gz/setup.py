#!/usr/bin/env python

# Copyright (c) 2018-2019 Iurii Kibalin   
# https://github.com/ikibalin/pycifstar  
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 
# * Neither the name "pycifstar" nor the names of its contributors may
#   be used to endorse or promote products derived from this software
#   without specific prior written permission.
# 
# This software is provided by the copyright holders and contributors "as
# is" and any express or implied warranties, including, but not limited
# to, the implied warranties of merchantability and fitness for a
# particular purpose are disclaimed. In no event shall the copyright owner
# or contributors be liable for any direct, indirect, incidental, special,
# exemplary, or consequential damages (including, but not limited to,
# procurement of substitute goods or services; loss of use, data, or
# profits; or business interruption) however caused and on any theory of
# liability, whether in contract, strict liability, or tort (including
# negligence or otherwise) arising in any way out of the use of this
# software, even if advised of the possibility of such damage.


from setuptools import setup, find_packages


long_description = '''\
PyCifStar is  a class library for  data manipulation  provided in 
the Self Defining Text Archival and Retrieval (STAR). The STAR syntax 
provides a way for simple, easy-to-comprehend, flexible and extensible 
data exchange. 

It is written in Python.

For more details, please go to the `github`_.

.. _`github`: https://github.com/ikibalin/pycifstar'''

#with open("readme.rst", 'r') as f:
#    long_description = f.read()

setup(
    name='pycifstar',
    version='0.2.2',
    description='PyCifStar is  a class library for  data manipulation  provided in the CIF/STAR File.',
    long_description = long_description,
    author='Iurii Kibalin',
    author_email='yurikibalin@outlook.com',
    url = 'https://github.com/ikibalin/pycifstar',
    license          = 'MIT License',
    keywords         = ['STAR', 'CIF'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],    
    packages=find_packages(),  #same as name
    install_requires=[]
)