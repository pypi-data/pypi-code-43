# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['slowmo']

package_data = \
{'': ['*']}

install_requires = \
['blessed>=1.15,<2.0', 'spinners>=0.0.23,<0.0.24']

setup_kwargs = {
    'name': 'slowmo',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Pedro Cattori',
    'author_email': 'pcattori@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
