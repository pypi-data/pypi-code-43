# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['chakra']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'chakra',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Raymond Ortserga',
    'author_email': 'codesage@live.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7,<3.0',
}


setup(**setup_kwargs)
