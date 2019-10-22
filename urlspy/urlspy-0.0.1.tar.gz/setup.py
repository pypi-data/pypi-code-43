# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['urlspy']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=2.0,<3.0', 'aiohttp>=3.6,<4.0', 'ruia>=0.6.2,<0.7.0']

setup_kwargs = {
    'name': 'urlspy',
    'version': '0.0.1',
    'description': '[WIP] Get information about URLs',
    'long_description': None,
    'author': 'Keshab Paudel',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
