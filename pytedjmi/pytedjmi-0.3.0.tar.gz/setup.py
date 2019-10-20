# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytedjmi']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.1,<3.0', 'pytest-django>=3.4,<4.0', 'pytest>=3.0,<4.0']

setup_kwargs = {
    'name': 'pytedjmi',
    'version': '0.3.0',
    'description': 'Test Django migrations through Pytest.',
    'long_description': '========================\nPytest Django Migrations\n========================\n\nversion number: 0.3.0\nauthor: Kit La Touche\n\nOverview\n--------\n\nTest Django migrations through Pytest.\n\nInstallation / Usage\n--------------------\n\nTo install use pip::\n\n    $ pip install pytedjmi\n\n\nOr clone the repo::\n\n    $ git clone https://github.com/wlonk/pytest-django-migrations.git\n    $ python setup.py install\n    \nContributing\n------------\n\nTBD\n\nExample\n-------\n\nTBD\n',
    'author': 'Kit La Touche',
    'author_email': 'kit@transneptune.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
