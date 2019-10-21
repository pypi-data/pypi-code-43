# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['decotra']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'decotra',
    'version': '0.0.0.dev0',
    'description': '',
    'long_description': None,
    'author': 'funwarioisii',
    'author_email': 'g231q026@s.iwate-pu.ac.jp',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
