# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['comment_formatter']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'comment-formatter',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'AlexPadron',
    'author_email': 'alexp@kensho.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
