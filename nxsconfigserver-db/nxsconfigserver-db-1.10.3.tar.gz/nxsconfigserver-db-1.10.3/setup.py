#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

""" setup.py for NXS configuration server """

import os

from distutils.core import setup

try:
    from sphinx.setup_command import BuildDoc
except Exception:
    BuildDoc = None


def read(fname):
    """ read the file

    :param fname: readme file name
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


#: (:obj:`str`) full release number
release = '1.10.3'
#: (:obj:`str`) release verion number
version = ".".join(release.split(".")[:2])
#: (:obj:`str`) program name
name = "NXSConfigServer-db"

#: (:obj:`dict` <:obj:`str` , any >`) metadata for distutils
SETUPDATA = dict(
    name="nxsconfigserver-db",
    version=release,
    author="Jan Kotanski",
    author_email="jankotan@gmail.com",
    description=("Configuration Server  DataBase"),
    license="GNU GENERAL PUBLIC LICENSE v3",
    keywords="configuration MySQL writer Tango server nexus data",
    url="https://github.com/jkotan/nexdatas/nxsconfigserver-db",
    data_files=[('share/nxsconfigserver', ['conf/my.cnf']),
                ('share/nxsconfigserver', ['conf/mysql_create.sql'])
                ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release)}},
    long_description=read('README.rst')
)


def main():
    """ the main function """
    setup(**SETUPDATA)


if __name__ == '__main__':
    main()
