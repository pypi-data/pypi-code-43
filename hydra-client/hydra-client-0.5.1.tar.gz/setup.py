# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['hydra_client']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.2,<20.0',
 'python-dateutil>=2.8,<3.0',
 'requests-oauthlib>=1.0,<2.0',
 'requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'hydra-client',
    'version': '0.5.1',
    'description': 'Client library for ORY Hydra (OAuth2 and OpenID Connect provider)',
    'long_description': None,
    'author': 'Simon Westphahl',
    'author_email': 'westphahl@gmail.com',
    'url': 'https://github.com/westphahl/hydra-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
