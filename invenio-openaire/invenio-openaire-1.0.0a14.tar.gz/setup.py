# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OpenAIRE service integration for Invenio repositories."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'invenio-celery>=1.1.0',
    'invenio-db>=1.0.1',
    'isort>=4.2.2',
    'jsonschema>=2.5.1',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

invenio_search_version = '1.2.0'

extras_require = {
    'docs': [
        'Sphinx>=1.4.2',
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
            'elasticsearch2',
            'elasticsearch5', 'elasticsearch6', 'elasticsearch7'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.7.0',
]

install_requires = [
    'Flask>=0.11.1',
    'Flask-BabelEx>=0.9.2',
    'Flask-Login>=0.3.2',
    'invenio-indexer>=1.1.0',
    'invenio-jsonschemas>=1.0.0',
    'invenio-pidstore>=1.0.0',
    'invenio-records-rest>=1.6.2',
    'invenio-records>=1.3.0',
    'jsonref>=0.1',
    'jsonresolver>=0.2.1',
    'requests>=2.9.1',
    'sickle>=0.5.0',
    'six>=1.10.0',
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_openaire', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-openaire',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio openaire',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-openaire',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_openaire = invenio_openaire:InvenioOpenAIRE',
        ],
        'invenio_base.api_apps': [
            'invenio_openaire = invenio_openaire:InvenioOpenAIRE',
        ],
        'invenio_celery.tasks': [
            'invenio_openaire = invenio_openaire.tasks',
        ],
        'invenio_i18n.translations': [
            'invenio_openaire = invenio_openaire',
        ],
        'invenio_jsonschemas.schemas': [
            'invenio_openaire = invenio_openaire.jsonschemas',
        ],
        'invenio_records.jsonresolver': [
            'invenio_openaire_funders = invenio_openaire.resolvers.funders',
            'invenio_openaire_grants = invenio_openaire.resolvers.grants',
        ],
        'invenio_search.mappings': [
            'funders = invenio_openaire.mappings',
            'grants = invenio_openaire.mappings',
        ],
        'invenio_pidstore.fetchers': [
            'openaire_grant_fetcher = invenio_openaire.fetchers:grant_fetcher',
            'openaire_funder_fetcher '
            '= invenio_openaire.fetchers:funder_fetcher'
        ],
        'invenio_pidstore.minters': [
            'openaire_grant_minter = invenio_openaire.minters:grant_minter',
            'openaire_funder_minter '
            '= invenio_openaire.minters:funder_minter'
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
        'Development Status :: 3 - Alpha',
    ],
)
