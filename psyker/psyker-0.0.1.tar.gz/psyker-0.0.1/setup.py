# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['psyker']

package_data = \
{'': ['*']}

install_requires = \
['psycopg2-binary>=2.8,<2.9']

setup_kwargs = {
    'name': 'psyker',
    'version': '0.0.1',
    'description': 'A psycopg2 library',
    'long_description': None,
    'author': 'Jacopo Cascioli',
    'author_email': 'jacopo@jacopocascioli.com',
    'url': 'https://github.com/strangemachines/psyker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
