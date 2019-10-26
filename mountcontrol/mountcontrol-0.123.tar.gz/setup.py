############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.7.4

#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
from setuptools import setup

setup(
    name='mountcontrol',
    version='0.123',
    packages=[
        'mountcontrol',
    ],
    python_requires='>=3.7.2',
    install_requires=[
        'PyQt5>=5.13',
        'numpy>=1.17',
        'skyfield>=1.13',
        'wakeonlan>=1.1.6',
    ],
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mworion',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ]
)
