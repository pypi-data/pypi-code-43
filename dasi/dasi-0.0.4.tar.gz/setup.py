# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dasi',
 'dasi.command_line',
 'dasi.cost',
 'dasi.design',
 'dasi.models',
 'dasi.utils',
 'dasi.utils.networkx']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.74,<2.0',
 'fire>=0.1,<0.2',
 'frozendict>=1.2,<2.0',
 'jsonschema>=3.1,<4.0',
 'loggable-jdv>=0.1.5,<0.2.0',
 'matplotlib>=3.1,<4.0',
 'more-itertools>=7.1,<8.0',
 'msgpack-numpy>=0.4.4,<0.5.0',
 'msgpack>=0.6.1,<0.7.0',
 'nest_asyncio>=1.0,<2.0',
 'networkx>=2.3,<3.0',
 'numpy>=1.17,<2.0',
 'pandas>=0.25.1,<0.26.0',
 'primer3plus>=1.0.5,<2.0.0',
 'pyblastbio>=0.4.1,<0.5.0',
 'seaborn>=0.9.0,<0.10.0',
 'sortedcontainers>=2.1,<3.0',
 'sympy>=1.4,<2.0',
 'tqdm>=4.32,<5.0',
 'uvloop>=0.12.2,<0.13.0']

entry_points = \
{'console_scripts': ['dasi = dasi:command_line.main']}

setup_kwargs = {
    'name': 'dasi',
    'version': '0.0.4',
    'description': '',
    'long_description': None,
    'author': 'jvrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
