# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['log_enricher']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'log-enricher',
    'version': '0.1.0',
    'description': 'Library to enrich structured logs',
    'long_description': None,
    'author': 'Arni Inaba Kjartansson',
    'author_email': 'arni@grid.is',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
