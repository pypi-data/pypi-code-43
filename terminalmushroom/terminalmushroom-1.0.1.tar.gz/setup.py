# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['terminalmushroom']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'terminalmushroom',
    'version': '1.0.1',
    'description': '',
    'long_description': None,
    'author': 'Coriander Pines',
    'author_email': '1647914-cvpines@users.noreply.gitlab.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
