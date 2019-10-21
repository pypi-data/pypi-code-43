# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pacurses']

package_data = \
{'': ['*'],
 'pacurses': ['constants/*',
              'gui/*',
              'gui/menus/*',
              'gui/widgets/*',
              'pulse_audio/*']}

install_requires = \
['urwid>=2.0,<3.0']

entry_points = \
{'console_scripts': ['pacurses = pacurses.main:main']}

setup_kwargs = {
    'name': 'pacurses',
    'version': '0.1.0',
    'description': 'A curses graphical interface to the PulseAudio sound system for the terminal.',
    'long_description': None,
    'author': 'Thore Weilbier',
    'author_email': 'thore@weilbier.net',
    'url': 'https://github.com/weilbith/pacurses',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
