# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['use_dir']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'use-dir',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mark Rawls',
    'author_email': 'markrawls96@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
