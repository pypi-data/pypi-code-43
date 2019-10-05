# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['underground', 'underground.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'google>=2.0,<3.0',
 'gtfs-realtime-bindings>=0.0.6,<0.0.7',
 'protobuf3-to-dict>=0.1.5,<0.2.0',
 'pydantic>=0.31.1,<0.32.0',
 'pytz>=2019.2,<2020.0',
 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['underground = underground.cli.cli:entry_point']}

setup_kwargs = {
    'name': 'underground',
    'version': '0.2.7',
    'description': '',
    'long_description': None,
    'author': 'Nolan Conaway',
    'author_email': 'nolanbconaway@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
