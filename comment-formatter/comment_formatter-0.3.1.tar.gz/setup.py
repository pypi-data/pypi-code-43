# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['comment_formatter']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'comment-formatter',
    'version': '0.3.1',
    'description': 'Formats comment blocks',
    'long_description': None,
    'author': 'AlexPadron',
    'author_email': 'alexander.f.padron@gmail.com',
    'url': 'https://github.com/AlexPadron/comment_formatter',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
