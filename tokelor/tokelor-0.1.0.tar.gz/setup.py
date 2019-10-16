# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tokelor']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'colorama>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['tokelor = tokelor.main:main']}

setup_kwargs = {
    'name': 'tokelor',
    'version': '0.1.0',
    'description': 'Visualize Python token stream produced by tokenize module.',
    'long_description': None,
    'author': 'Kirill Borisov',
    'author_email': 'lensvol@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
