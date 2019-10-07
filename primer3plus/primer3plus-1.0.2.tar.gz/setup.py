# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['primer3plus', 'primer3plus.design', 'primer3plus.params', 'primer3plus.utils']

package_data = \
{'': ['*']}

install_requires = \
['loggable-jdv>=0.1.2,<0.2.0', 'primer3-py>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'primer3plus',
    'version': '1.0.2',
    'description': 'An easy-to-use Python API for Primer3 primer design.',
    'long_description': None,
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://github.com/jvrana/primer3-py-plus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
