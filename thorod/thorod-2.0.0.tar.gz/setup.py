# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['thorod']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'attrs>=18.2,<19.4',
 'colorama<1.0.0',
 'pendulum>=2.0,<3.0',
 'pprintpp<1.0.0',
 'sortedcontainers>=2.0,<3.0',
 'tbm-utils>=1.0,<2.0',
 'tomlkit>=0.5,<0.6',
 'tqdm>=4.19,<5.0']

extras_require = \
{'dev': ['flake8>=3.5,<4.0',
         'flake8-builtins>=1.0,<2.0',
         'flake8-comprehensions>=2.0,<3.0',
         'flake8-import-order>=0.18,<0.19',
         'flake8-import-order-tbm>=1.0.0,<2.0.0',
         'nox>=2019,<2020',
         'sphinx>=2.0,<3.0',
         'sphinx-argparse>=0.2,<0.3'],
 'doc': ['sphinx>=2.0,<3.0', 'sphinx-argparse>=0.2,<0.3'],
 'lint': ['flake8>=3.5,<4.0',
          'flake8-builtins>=1.0,<2.0',
          'flake8-comprehensions>=2.0,<3.0',
          'flake8-import-order>=0.18,<0.19',
          'flake8-import-order-tbm>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['thorod = thorod.cli:run']}

setup_kwargs = {
    'name': 'thorod',
    'version': '2.0.0',
    'description': 'A CLI utility for torrent creation and manipulation.',
    'long_description': "# thorod\n\n[![PyPI](https://img.shields.io/pypi/v/thorod.svg?label=PyPI)](https://pypi.org/project/thorod/)\n![](https://img.shields.io/badge/Python-3.6%2B-blue.svg)  \n[![Travis](https://img.shields.io/travis/thebigmunch/thorod.svg?label=Travis)](https://travis-ci.org/thebigmunch/thorod)  \n[![Docs - Stable](https://img.shields.io/readthedocs/thorod/stable.svg?label=Docs%20%28Stable%29)](https://thorod.readthedocs.io/en/stable/)\n[![Docs - Latest](https://img.shields.io/readthedocs/thorod/latest.svg?label=Docs%20%28Latest%29)](https://thorod.readthedocs.io/en/latest/)\n\n[thorod](https://github.com/thebigmunch/thorod) is a CLI utility for torrent creation and manipulation.\n\n## What's a thorod?\n\nThorod means torrent (of water) in the Tolkien Elvish language of Sindarin.\n\n## Why use thorod?\n\nThere are many CLI torrent utilities out there, so here are some unique or notable features of thorod:\n\n* All torrents are unique; a random salt is added to all created/xseeded torrents.\n* Supports trackers on the same tier.\n* Type less with tracker abbreviations.\n\t* Includes a number of open public trackers by default.\n\t* Includes auto generated open and random abbreviations to help balance load between open public trackers.\n\t* Users can list/add/remove their own tracker abbreviations directly from CLI as well as manually editing config file.\n* Generate magnet links on creation or on command.\n* Has an xseed command to generate a cross-seedable torrent without re-hashing files.\n* View information about a torrent file in the terminal, rather than adding it to a torrent client.\n* Simple automatic piece size calculation from 16 KiB to 32 MiB on by default. Users can set manually by option.\n* Supports source key in info dict used by private trackers.\n\n\n## Installation\n\n``pip install -U thorod``\n\n\n## Usage\n\nFor the release version, see the [stable docs](https://thorod.readthedocs.io/en/stable/).  \nFor the development version, see the [latest docs](https://thorod.readthedocs.io/en/latest/).\n\n\n## Appreciation\n\nShowing appreciation is always welcome.\n\n#### Thank\n\n[![Say Thanks](https://img.shields.io/badge/thank-thebigmunch-blue.svg?style=flat-square)](https://saythanks.io/to/thebigmunch)\n\nGet your own thanks inbox at [SayThanks.io](https://saythanks.io/).\n\n#### Contribute\n\n[Contribute](https://github.com/thebigmunch/thorod/blob/master/.github/CONTRIBUTING.md) by submitting bug reports, feature requests, or code.\n\n#### Help Others/Stay Informed\n\n[Discourse forum](https://forum.thebigmunch.me/)\n\n#### Referrals/Donations\n\n[![Digital Ocean](https://img.shields.io/badge/Digital_Ocean-referral-orange.svg?style=flat-square)](https://bit.ly/DigitalOcean-tbm-referral) [![Namecheap](https://img.shields.io/badge/Namecheap-referral-orange.svg?style=flat-square)](http://bit.ly/Namecheap-tbm-referral) [![PayPal](https://img.shields.io/badge/PayPal-donate-brightgreen.svg?style=flat-square)](https://bit.ly/PayPal-thebigmunch)\n",
    'author': 'thebigmunch',
    'author_email': 'mail@thebigmunch.me',
    'url': 'https://github.com/thebigmunch/thorod',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
