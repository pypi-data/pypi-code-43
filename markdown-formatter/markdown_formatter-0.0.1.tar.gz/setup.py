# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['markdown_formatter']

package_data = \
{'': ['*']}

install_requires = \
['black>=18.3-alpha.0,<19.0',
 'click>=7.0,<8.0',
 'cython>=0.29.13,<0.30.0',
 'mistune>=0.8.4,<0.9.0']

entry_points = \
{'console_scripts': ['markdown_formatter = markdown_formatter.cli:run_main']}

setup_kwargs = {
    'name': 'markdown-formatter',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Trim21',
    'author_email': 'i@trim21.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
