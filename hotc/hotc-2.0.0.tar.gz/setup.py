# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hotc']

package_data = \
{'': ['*'], 'hotc': ['data/*']}

install_requires = \
['pandas<1', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'hotc',
    'version': '2.0.0',
    'description': 'A Python 3.6+ library to get walking counts for central Auckland, New Zealand from the Heart of the City API. The API has access to counts from 2012-01-23 to the present.',
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
