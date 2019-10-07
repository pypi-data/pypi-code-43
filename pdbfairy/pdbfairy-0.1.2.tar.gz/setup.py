# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pdbfairy', 'pdbfairy.commands']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.74,<2.0',
 'click>=7.0,<8.0',
 'memoized>=0.3.0,<0.4.0',
 'numpy>=1.16,<1.17']

entry_points = \
{'console_scripts': ['pdbfairy = pdbfairy.main:main']}

setup_kwargs = {
    'name': 'pdbfairy',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Danny Roberts',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
