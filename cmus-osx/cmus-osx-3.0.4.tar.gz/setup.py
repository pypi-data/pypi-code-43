# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cmus_osx']

package_data = \
{'': ['*'], 'cmus_osx': ['payload/*', 'resource/*']}

install_requires = \
['Pillow>=6.1.0,<7.0.0',
 'click>=7.0,<8.0',
 'mutagen>=1.42,<2.0',
 'pyobjc>=5.2,<6.0']

entry_points = \
{'console_scripts': ['cmus-osx = cmus_osx:entrypoint']}

setup_kwargs = {
    'name': 'cmus-osx',
    'version': '3.0.4',
    'description': 'Adds track change notifications, and media key support to cmus.',
    'long_description': '<img align="right" src="https://user-images.githubusercontent.com/9287847/33808557-f03eef40-dde8-11e7-8951-68350df85a70.gif" width="350"/>\n\n<p>\xe2\x80\x8b</p>\n\n<h1><kbd>\xe2\x96\xb6</kbd> cmus-osx</h1>\n\n![Python version support: 3.7](https://img.shields.io/badge/python-3.7-limegreen.svg)\n[![PyPI version](https://badge.fury.io/py/cmus-osx.svg)](https://badge.fury.io/py/cmus-osx)\n![License: MIT](https://img.shields.io/badge/license-MIT-limegreen.svg)\n[![CircleCI](https://circleci.com/gh/PhilipTrauner/cmus-osx.svg?style=svg)](https://circleci.com/gh/PhilipTrauner/cmus-osx)\n\n**cmus-osx** adds track change notifications, and media key support to [*cmus*](https://cmus.github.io/) (*macOS* only).\n\n## Installation\nmacOS automatically launches iTunes on media key presses.\nInstalling [noTunes](https://github.com/tombonez/noTunes/releases/tag/v2.0) is the recommended solution to prevent this from happening.\n\n```bash\npip3 install cmus-osx\ncmus-osx install\n```\n\n**cmus-osx** supports virtual environments natively, so installing it via `pipx` (or basically any other virtual environment manager) works just as well.\n\n### Uninstall\n```\ncmus-osx uninstall\npip3 uninstall cmus-osx\n```\n\n#### pyenv\nFramework building has to be enabled, otherwise notifications cannot be created.\n```bash\nexport PYTHON_CONFIGURE_OPTS="--enable-framework"\n```\n\n## Configuration\n```\ncmus-osx config\n```\n\n### Credits\n* [azadkuh](https://github.com/azadkuh): all versions up to and including v1.2.0\n* [PhilipTrauner](https://github.com/PhilipTrauner): all following versions\n',
    'author': 'Philip Trauner',
    'author_email': 'philip.trauner@arztpraxis.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
