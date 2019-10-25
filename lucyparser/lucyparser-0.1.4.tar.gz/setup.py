# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lucyparser']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'lucyparser',
    'version': '0.1.4',
    'description': 'Lucene-like syntax parser',
    'long_description': None,
    'author': 'Timur',
    'author_email': 'timur.makarchuk@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
