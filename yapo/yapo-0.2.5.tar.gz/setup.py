# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['yapo', 'yapo._index', 'yapo._portfolio', 'yapo._sources', 'yapo.common']

package_data = \
{'': ['*']}

install_requires = \
['PyContracts>=1.8,<2.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.24,<0.25',
 'pinject>=0.14.1,<0.15.0',
 'typing_extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'yapo',
    'version': '0.2.5',
    'description': 'Flexible and easy-to-use Python library for analysis & manipulation with financial & economic data',
    'long_description': 'We renamed **yapo** to **cifrum** and moved it to https://cifrum.io.\n',
    'author': 'Alexander Myltsev',
    'author_email': None,
    'url': 'https://github.com/okama-io/yapo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
