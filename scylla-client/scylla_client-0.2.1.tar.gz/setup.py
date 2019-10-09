# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['scylla']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0', 'sitri>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'scylla-client',
    'version': '0.2.1',
    'description': 'Scylla - client for charybdis permission manager',
    'long_description': None,
    'author': 'Alexander Lavrov',
    'author_email': 'egnod@ya.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
