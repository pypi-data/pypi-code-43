# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pfun']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'pfun',
    'version': '0.5.0',
    'description': '',
    'long_description': None,
    'author': 'Sune Debel',
    'author_email': 'sad@archii.ai',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
