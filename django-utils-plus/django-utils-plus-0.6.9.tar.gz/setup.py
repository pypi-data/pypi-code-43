# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['utils_plus',
 'utils_plus.management',
 'utils_plus.management.commands',
 'utils_plus.migrations',
 'utils_plus.templatetags',
 'utils_plus.utils',
 'utils_plus.views']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.1,<3.0']

setup_kwargs = {
    'name': 'django-utils-plus',
    'version': '0.6.9',
    'description': 'A reusable Django app with small set of utilities for urls, viewsets, commands and more',
    'long_description': None,
    'author': 'jnoortheen',
    'author_email': 'jnoortheen@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
