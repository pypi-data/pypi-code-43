# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['yotuyu']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17,<2.0',
 'optuna>=0.17.1,<0.18.0',
 'pandas>=0.25.2,<0.26.0',
 'scikit-learn>=0.21.3,<0.22.0']

setup_kwargs = {
    'name': 'yotuyu',
    'version': '0.0.0.dev0',
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
