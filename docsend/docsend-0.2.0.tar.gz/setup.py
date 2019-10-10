# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['docsend']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'pillow>=5.3,<6.0', 'requests-html>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['docsend = docsend.cli:main']}

setup_kwargs = {
    'name': 'docsend',
    'version': '0.2.0',
    'description': 'convert docsend to pdf or png sequence',
    'long_description': None,
    'author': 'banteg',
    'author_email': 'banteeg@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
