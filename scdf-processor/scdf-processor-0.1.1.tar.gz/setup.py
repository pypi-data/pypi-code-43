# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['scdf_processor']

package_data = \
{'': ['*']}

install_requires = \
['kafka-python>=1.4,<2.0']

setup_kwargs = {
    'name': 'scdf-processor',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
