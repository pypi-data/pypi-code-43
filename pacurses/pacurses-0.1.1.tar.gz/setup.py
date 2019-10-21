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
    'version': '0.1.1',
    'description': 'A curses graphical interface to the PulseAudio sound system for the terminal.',
    'long_description': '# Pacurses\n\nA curses graphical interface to the\n[PulseAudio](https://www.freedesktop.org/wiki/Software/PulseAudio) sound system\nfor the terminal.\n\n![Main Menu](docs/screenshots/menu_main.png)\n![Output Volume Menu](docs/screenshots/menu_volume_outputs.png)\n\n## Installation\n\n### PulseAudio\n\nIn the end, `pacurses` is only a graphical interface which is using `pacmd`\nto communicate with the _PulseAudio_ daemon. Therefore make sure that both are\ninstalled and running on your machine.\n\n- [ArchLinux](https://wiki.archlinux.org/index.php/PulseAudio#Installation)\n- [Ubuntu](https://wiki.ubuntu.com/PulseAudio)\n- ...\n\n### Pacurses\n\nInstall it globally with [pip](https://pip.pypa.io/en/stable):\n\n```shell\n$ pip install pacurses\n```\n\nExecute always the most recent version with [pipx](https://pipxproject.github.io/pipx/):\n\n```shell\n$ pipx run pacurses\n```\n',
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
