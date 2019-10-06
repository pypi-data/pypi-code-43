# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': '.'}

packages = \
['potion_client']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.0,<4.0', 'requests>=2.5,<3.0', 'six>=1.12,<2.0']

setup_kwargs = {
    'name': 'turmalin',
    'version': '2.5.1',
    'description': 'A client for APIs written in Flask-Potion',
    'long_description': None,
    'author': 'Lars Schöning',
    'author_email': 'lars@lyschoening.de',
    'url': 'https://github.com/biosustain/potion-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
