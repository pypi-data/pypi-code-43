# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['kattiskitten']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4==4.8.1', 'click==7.0', 'colorful==0.5.4', 'requests==2.22.0']

entry_points = \
{'console_scripts': ['kk = kattiskitten:main']}

setup_kwargs = {
    'name': 'kattiskitten',
    'version': '0.1.0',
    'description': 'Kattis CLI - Easily download, test and submit kattis problems',
    'long_description': None,
    'author': 'Felix Qvist',
    'author_email': 'felix.qvist@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
