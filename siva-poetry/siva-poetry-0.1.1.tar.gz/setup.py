# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['siva_poetry']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.0,<3.0']

setup_kwargs = {
    'name': 'siva-poetry',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'siva',
    'author_email': 'sivakon@outlook.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
