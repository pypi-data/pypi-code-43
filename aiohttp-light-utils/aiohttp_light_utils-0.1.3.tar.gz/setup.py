# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aiohttp_light_utils']

package_data = \
{'': ['*']}

install_requires = \
['trafaret-config>=2.0,<3.0', 'ujson>=1.35,<2.0']

setup_kwargs = {
    'name': 'aiohttp-light-utils',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Khaziev Radik',
    'author_email': 'xazrad@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
