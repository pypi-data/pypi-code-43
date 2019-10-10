# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['make_gtfs']

package_data = \
{'': ['*']}

install_requires = \
['gtfs_kit>=2.0,<3.0']

setup_kwargs = {
    'name': 'make-gtfs',
    'version': '2.1.0',
    'description': 'A Python 3.6+ library to build GTFS feeds from basic route information.',
    'long_description': None,
    'author': 'Alex Raichev',
    'author_email': 'araichev@mrcagney.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
