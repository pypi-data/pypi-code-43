# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hatchbuck']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'pyhatchbuck',
    'version': '0.2',
    'description': 'Python library for Hatchbuck API',
    'long_description': None,
    'author': 'Jacob Senecal',
    'author_email': 'jacob.senecal@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7,<3.0',
}


setup(**setup_kwargs)
