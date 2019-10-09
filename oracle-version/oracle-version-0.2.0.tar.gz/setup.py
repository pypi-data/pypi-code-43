# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': '.'}

packages = \
['src']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'oracle-version',
    'version': '0.2.0',
    'description': 'Oracle - until for intresting versions name',
    'long_description': None,
    'author': 'Alexander Lavrov',
    'author_email': 'egnod@ya.ru',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
