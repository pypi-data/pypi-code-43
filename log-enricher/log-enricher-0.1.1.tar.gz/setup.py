# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['log_enricher']

package_data = \
{'': ['*']}

install_requires = \
['python-json-logger>=0.1.11,<0.2.0']

setup_kwargs = {
    'name': 'log-enricher',
    'version': '0.1.1',
    'description': 'Library to enrich structured logs',
    'long_description': None,
    'author': 'Arni Inaba Kjartansson',
    'author_email': 'arni@grid.is',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
