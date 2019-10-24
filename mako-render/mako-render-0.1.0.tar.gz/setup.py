# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mako_render']

package_data = \
{'': ['*']}

install_requires = \
['mako>=1.1,<2.0']

entry_points = \
{'console_scripts': ['mako_render = mako_render:main']}

setup_kwargs = {
    'name': 'mako-render',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'gfreezy',
    'author_email': 'gfreezy@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
