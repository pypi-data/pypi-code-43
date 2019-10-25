# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytus']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'pytus',
    'version': '0.2.1',
    'description': 'yet another tus (resumable file upload protocol) client in python',
    'long_description': None,
    'author': 'yatmanov',
    'author_email': 'yatmanov@megaputer.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
