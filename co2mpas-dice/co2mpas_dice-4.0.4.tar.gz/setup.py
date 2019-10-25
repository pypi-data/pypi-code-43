#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import io
import os.path as osp

name = 'co2mpas_dice'
mydir = osp.dirname(__file__)


# Version-trick to have version-info in a single place,
# taken from: http://stackoverflow.com/questions/2058802/how-can-i-get-the-
# version-defined-in-setup-py-setuptools-in-my-package
##
def read_project_version():
    fglobals = {}
    with io.open(osp.join(mydir, name, '_version.py'), encoding='UTF-8') as fd:
        exec(fd.read(), fglobals)  # To read __version__
    return fglobals['__version__']


proj_ver = read_project_version()
url = 'https://github.com/JRCSTU/DICE'
download_url = '%s/tarball/v%s' % (url, proj_ver)

if __name__ == '__main__':
    import os
    from setuptools import setup, find_packages

    exclude = ['requirements']
    if os.environ.get('DICE_SERVER') != 'True':
        exclude.append('co2mpas_dice.server*')
    setup(
        name=name,
        version=proj_ver,
        packages=find_packages(exclude=exclude),
        url=url,
        download_url=download_url,
        license='EUPL 1.1+',
        author='Vincenzo Arcidiacono',
        author_email='vinci1it2000@gmail.com',
        install_requires=[
            'cryptography',
            'lmfit',
            'numpy',
            'pyyaml',
            'schedula',
        ],
        python_requires='>=3.7',
        package_data={
            'co2mpas_dice.server': ['templates/*', 'keys/*', 'app.ini'],
            'co2mpas_dice.server.mail': ['templates/*'],
            'co2mpas_dice.server.validate': ['*.json']
        },
        extras_require={
            'server': [
                'click',
                'click-log',
                'docutils',
                'flask',
                'gunicorn',
                'jinja2',
                'jsonschema',
                'mysql-connector-python',
                'pandas',
                'tabulate',
                'werkzeug'
            ],
            'co2mpas': ['scipy']
        },
        entry_points={
            'console_scripts': [
                '%(p)s = %(p)s.server.cli:cli' % {'p': name},
            ],
        },
        options={
            'bdist_wheel': {
                'universal': True,
            },
        },
        platforms=['any'],
    )
