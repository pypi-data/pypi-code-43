# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['wacryptolib']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'decorator>=4.4,<5.0',
 'jsonrpc-requests>=0.4.0,<0.5.0',
 'pycryptodome>=3.9,<4.0',
 'pymongo>=3.9,<4.0',
 'schema>=0.7.0,<0.8.0']

setup_kwargs = {
    'name': 'wacryptolib',
    'version': '0.3',
    'description': 'Witness Angel Cryptolib',
    'long_description': 'Witness Angel Cryptolib\n#############################\n\n.. image:: https://travis-ci.com/WitnessAngel/witness-angel-cryptolib.svg?branch=master\n    :target: https://travis-ci.com/WitnessAngel/witness-angel-cryptolib\n\nThis lib gathers utilities to generate keys, and encrypt/decrypt/sign container data, for the\nWitness Angel system.\n\nIt also provides utilities for webservices and their error handling.\n\n\n',
    'author': 'Pascal Chambon',
    'author_email': None,
    'url': 'https://github.com/WitnessAngel/witness-angel-cryptolib',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
