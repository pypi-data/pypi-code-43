# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['square']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'google-api-python-client>=1.7,<2.0',
 'google>=2.0,<3.0',
 'jsonpatch>=1.24,<2.0',
 'pyyaml>=5.1,<6.0',
 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['square = square.main:main']}

setup_kwargs = {
    'name': 'kubernetes-square',
    'version': '0.16.1',
    'description': '',
    'long_description': None,
    'author': 'Oliver Nagy',
    'author_email': 'olitheolix@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
