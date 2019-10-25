# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytezos',
 'pytezos.michelson',
 'pytezos.operation',
 'pytezos.rpc',
 'pytezos.tools']

package_data = \
{'': ['*'], 'pytezos': ['standards/*'], 'pytezos.tools': ['templates/*']}

install_requires = \
['base58>=1.0.3,<2.0.0',
 'fastecdsa>=1.7.1,<2.0.0',
 'fire',
 'loguru',
 'mnemonic',
 'netstruct',
 'pendulum',
 'ply',
 'pyblake2>=1.1.2,<2.0.0',
 'pysodium>=0.7.1,<0.8.0',
 'requests>=2.21.0,<3.0.0',
 'secp256k1>=0.13.2,<0.14.0',
 'simplejson',
 'tqdm']

entry_points = \
{'console_scripts': ['pytezos = pytezos:cli.main']}

setup_kwargs = {
    'name': 'pytezos',
    'version': '2.1.0',
    'description': 'Python toolkit for Tezos',
    'long_description': "# PyTezos\n\n[![PyPI version](https://badge.fury.io/py/pytezos.svg?)](https://badge.fury.io/py/pytezos)\n[![Build Status](https://travis-ci.org/baking-bad/pytezos.svg?branch=master)](https://travis-ci.org/baking-bad/pytezos)\n[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](https://www.python.org)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\nPython SDK for Tezos: RPC, cryptography, operations, smart contract interaction\n\n### Requirements\n\n* git\n* python 3.6+\n* pip 19.0.1+\n\nYou will also probably need to install several cryptographic packets.\n\n#### Linux\n\nUse apt or your favourite package manager:\n```\n$ sudo apt install libsodium-dev libsecp256k1-dev libgmp-dev\n```\n\n#### MacOS\n\nUse homebrew:\n```\n$ brew tap cuber/homebrew-libsecp256k1\n$ brew install libsodium libsecp256k1 gmp\n```\n\n#### Windows\n\nThe recommended way is to use WSL and then follow the instructions for Linux,\nbut if you feel lucky you can try to install natively:\n\n1. Install MinGW from [https://osdn.net/projects/mingw/](https://osdn.net/projects/mingw/)\n2. Make sure `C:\\MinGW\\bin` is added to your `PATH`\n3. Download the latest libsodium-X.Y.Z-msvc.zip from [https://download.libsodium.org/libsodium/releases/](https://download.libsodium.org/libsodium/releases/).\n4. Extract the Win64/Release/v143/dynamic/libsodium.dll from the zip file\n5. Copy libsodium.dll to C:\\Windows\\System32\\libsodium.dll\n\n### Installation\n\n```\n$ pip install pytezos\n```\n\n#### Google Colab\n\n`````python\n>>> !apt apt install libsodium-dev libsecp256k1-dev libgmp-dev\n>>> !pip install pytezos\n`````\n\n### Usage\n\nRead [quick start guide](https://baking-bad.github.io/pytezos), or just enjoy surfing the interactive documentation using Python console/Jupyter:\n```python\n>>> from pytezos import pytezos\n>>> pytezos\n<pytezos.client.PyTezosClient object at 0x7f904cf339e8>\n\nProperties\n.key  # tz1grSQDByRpnVs7sPtaprNZRp531ZKz6Jmm\n.shell  # https://tezos-dev.cryptonomic-infra.tech/ (alphanet)\n\nHelpers\n.account()\n.activate_account()\n.ballot()\n.contract()\n.delegation()\n.double_baking_evidence()\n.double_endorsement_evidence()\n.endorsement()\n.operation()\n.operation_group()\n.origination()\n.proposals()\n.reveal()\n.seed_nonce_revelation()\n.transaction()\n.using()\n```\n\n### Publications\n\n* Pytezos 2.0 release with embedded docs and smart contract interaction engine  \nhttps://medium.com/coinmonks/high-level-interface-for-michelson-contracts-and-not-only-7264db76d7ae\n\n* Materials from TQuorum:Berlin workshop - building an app on top of PyTezos and ConseilPy  \nhttps://medium.com/coinmonks/atomic-tips-berlin-workshop-materials-c5c8ee3f46aa\n\n* Materials from the EETH hackathon - setting up a local development infrastructure, deploying and interacting with a contract  \nhttps://medium.com/tezoscommons/preparing-for-the-tezos-hackathon-with-baking-bad-45f2d5fca519\n\n* Introducing integration testing engine  \nhttps://medium.com/tezoscommons/testing-michelson-contracts-with-pytezos-513718499e93\n\n\n### About\nThe project was initially started by Arthur Breitman, now it's maintained by Baking Bad team.\nPyTezos development is supported by Tezos Foundation.\n",
    'author': 'Michael Zaikin',
    'author_email': 'mz@baking-bad.org',
    'url': 'https://baking-bad.github.io/pytezos/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
