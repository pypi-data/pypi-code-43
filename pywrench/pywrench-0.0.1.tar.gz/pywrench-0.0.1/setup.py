# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pywrench']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pywrench',
    'version': '0.0.1',
    'description': 'Pluggable configuration system',
    'long_description': None,
    'author': 'Robert Wikman',
    'author_email': 'rbw@vault13.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
