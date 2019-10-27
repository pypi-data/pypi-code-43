# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['attrs_validation_type']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'attrs-validation-type',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'masahitojp',
    'author_email': 'randomstep@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
