# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyfml', 'pyfml.internal']

package_data = \
{'': ['*']}

install_requires = \
['purl>=1.5,<2.0', 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'pyfml',
    'version': '0.1.11',
    'description': 'python factory meta language',
    'long_description': None,
    'author': 'Ben G',
    'author_email': 'ben.gordon@toasttab.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
