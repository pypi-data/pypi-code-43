# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module integrating Invenio repositories and OpenDefinition."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'httpretty>=0.8.14',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=3.3.1',
]

invenio_search_version = '1.2.0'

extras_require = {
    'docs': [
        'Sphinx>=1.6.7',
    ],
    'elasticsearch2': [
        'invenio-search[elasticsearch2]>={}'.format(invenio_search_version),
    ],
    'elasticsearch5': [
        'invenio-search[elasticsearch5]>={}'.format(invenio_search_version),
    ],
    'elasticsearch6': [
        'invenio-search[elasticsearch6]>={}'.format(invenio_search_version),
    ],
    'elasticsearch7': [
        'invenio-search[elasticsearch7]>={}'.format(invenio_search_version),
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in (
            'elasticsearch2', 'elasticsearch5',
            'elasticsearch6', 'elasticsearch7'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.7.0',
]

install_requires = [
    'Flask>=0.11.1',
    'click>=6.4',
    'flask-celeryext>=0.3.0',
    'invenio-indexer>=1.1.0',
    'invenio-jsonschemas>=1.0.0',
    'invenio-pidstore>=1.0.0',
    'invenio-records>=1.0.0',
    'invenio-records-rest>=1.6.2',
    'jsonref>=0.1',
    'jsonresolver>=0.2.1',
    'jsonschema>=2.5.1',
    'requests>=2.9.1',
    'invenio-db[versioning]>=1.0.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_opendefinition', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-opendefinition',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-opendefinition',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_opendefinition = '
            'invenio_opendefinition:InvenioOpenDefinition',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_opendefinition',
        ],
        'invenio_records.jsonresolver': [
            'invenio_opendefinition = invenio_opendefinition.resolvers',
        ],
        'invenio_celery.tasks': [
            'invenio_opendefinition = invenio_opendefinition.tasks',
        ],
        'invenio_jsonschemas.schemas': [
            'invenio_opendefinition = invenio_opendefinition.jsonschemas',
        ],
        'invenio_search.mappings': [
            'licenses = invenio_opendefinition.mappings',
        ],
        'invenio_pidstore.fetchers': [
            'opendefinition_license_fetcher = '
            'invenio_opendefinition.fetchers:license_fetcher',
        ],
        'invenio_pidstore.minters': [
            'opendefinition_license_minter = '
            'invenio_opendefinition.minters:license_minter',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
    ],
)
