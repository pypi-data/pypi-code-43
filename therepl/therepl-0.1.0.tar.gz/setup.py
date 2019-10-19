# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['therepl']

package_data = \
{'': ['*']}

install_requires = \
['flask>=1.1,<2.0', 'ipython>=7.8,<8.0']

setup_kwargs = {
    'name': 'therepl',
    'version': '0.1.0',
    'description': 'IPython extension to switch and edit python modules on fly either from the repl or from IDE.',
    'long_description': None,
    'author': 'Alexander Artemenko',
    'author_email': 'svetlyak.40wt@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
