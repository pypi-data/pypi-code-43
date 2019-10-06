# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['thumbgen']

package_data = \
{'': ['*']}

install_requires = \
['PyGObject>=3.34,<4.0',
 'click>=7.0,<8.0',
 'loguru>=0.3.2,<0.4.0',
 'tqdm>=4.36,<5.0']

entry_points = \
{'console_scripts': ['fix = scripts:fix', 'thumbgen = thumbgen.thumbgen:main']}

setup_kwargs = {
    'name': 'thumbgen',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mudassir Khan',
    'author_email': 'mudassirkhan19@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
