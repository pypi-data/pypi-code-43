# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['classes', 'classes.contrib', 'classes.contrib.mypy']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'classes',
    'version': '0.0.1',
    'description': 'Type-safe typeclasses and ad-hoc polymorphism for Python',
    'long_description': '',
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://classes.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
