# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dli_scrapping_lib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dli-scrapping-lib',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'dli',
    'author_email': 'davidli012345@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
