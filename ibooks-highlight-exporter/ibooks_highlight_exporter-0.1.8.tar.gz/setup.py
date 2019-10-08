# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ibooks_highlight_exporter']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0', 'lxml>=4.4,<5.0']

entry_points = \
{'console_scripts': ['ibooks_higlight_exporter = '
                     'ibooks_highlight_exporter:main.export']}

setup_kwargs = {
    'name': 'ibooks-highlight-exporter',
    'version': '0.1.8',
    'description': 'Export highlights from your iBooks to HTML including chapter titles',
    'long_description': None,
    'author': 'Olga Andreeva',
    'author_email': 'indmajor64@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
