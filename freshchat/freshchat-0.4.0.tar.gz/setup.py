# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['freshchat', 'freshchat.client', 'freshchat.models', 'freshchat.webhook']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.5,<4.0',
 'cafeteria>=0.19,<0.20',
 'pycrypto>=2.6,<3.0',
 'pytest-cov>=2.7,<3.0']

setup_kwargs = {
    'name': 'freshchat',
    'version': '0.4.0',
    'description': 'A library provide a http client for Freshchat API',
    'long_description': '# FreshChat Client\nA library provide a http client for Freshchat API \n\n## Installation\n`poetry install python-freshchat`\n',
    'author': 'Twyla Engineering',
    'author_email': 'software@twyla.ai',
    'url': 'https://github.com/twyla-ai/python-freshchat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
