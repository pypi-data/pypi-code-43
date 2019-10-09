# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['beancount_ing_diba']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'beancount-ing-diba',
    'version': '0.2.1',
    'description': 'Beancount Importer for ING-DiBa (DE) CSV exports',
    'long_description': None,
    'author': 'Siddhant Goel',
    'author_email': 'me@sgoel.org',
    'url': 'https://github.com/siddhantgoel/beancount-ing-diba',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
