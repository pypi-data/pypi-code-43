# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['decotra']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.10,<2.0', 'numpy>=1.17,<2.0']

setup_kwargs = {
    'name': 'decotra',
    'version': '0.0.4.dev0',
    'description': '',
    'long_description': None,
    'author': 'funwarioisii',
    'author_email': 'mottirioisii@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
