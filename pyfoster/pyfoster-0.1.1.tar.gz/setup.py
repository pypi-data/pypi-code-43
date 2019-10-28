# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyfoster']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyfoster',
    'version': '0.1.1',
    'description': 'Python Utility Functions on Steroid',
    'long_description': None,
    'author': 'rednafi',
    'author_email': 'redowan.nafi@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
