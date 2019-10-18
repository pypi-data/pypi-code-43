# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mannequin']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17,<2.0']

setup_kwargs = {
    'name': 'mannequin',
    'version': '0.0.1',
    'description': 'Neural network implementation in pure python',
    'long_description': None,
    'author': 'Kracekumar',
    'author_email': 'me@kracekumar',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
