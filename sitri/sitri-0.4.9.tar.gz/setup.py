# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sitri', 'sitri.config', 'sitri.contrib', 'sitri.credentials']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sitri',
    'version': '0.4.9',
    'description': 'Library for one endpoint config and credentials managment',
    'long_description': None,
    'author': 'Alexander Lavrov',
    'author_email': 'egnod@ya.ru',
    'url': 'https://github.com/Egnod/sitri',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
