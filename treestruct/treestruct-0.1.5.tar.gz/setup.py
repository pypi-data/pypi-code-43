# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['treestruct']

package_data = \
{'': ['*']}

install_requires = \
['graphviz>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'treestruct',
    'version': '0.1.5',
    'description': 'Simplify the task of creating, traversing, manipulating and visualizing tree structures',
    'long_description': None,
    'author': 'Shady Rafehi',
    'author_email': 'shadyrafehi@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
