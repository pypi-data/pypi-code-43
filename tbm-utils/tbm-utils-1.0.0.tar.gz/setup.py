# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['tbm_utils']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.3', 'pendulum>=2.0,<3.0', 'pprintpp<1.0.0', 'wrapt>=1.0,<2.0']

extras_require = \
{'dev': ['coverage>=4.5,<5.0',
         'flake8>=3.5,<4.0',
         'flake8-builtins>=1.0,<2.0',
         'flake8-comprehensions>=2.0,<3.0',
         'flake8-import-order>=0.18,<0.19',
         'flake8-import-order-tbm>=1.0.0,<2.0.0',
         'nox>=2019,<2020',
         'pytest>=4.0,<6.0',
         'sphinx>=2.0,<3.0'],
 'doc': ['sphinx>=2.0,<3.0'],
 'lint': ['flake8>=3.5,<4.0',
          'flake8-builtins>=1.0,<2.0',
          'flake8-comprehensions>=2.0,<3.0',
          'flake8-import-order>=0.18,<0.19',
          'flake8-import-order-tbm>=1.0.0,<2.0.0'],
 'test': ['coverage>=4.5,<5.0', 'nox>=2019,<2020', 'pytest>=4.0,<6.0']}

setup_kwargs = {
    'name': 'tbm-utils',
    'version': '1.0.0',
    'description': 'A commonly-used set of utilities used by me (thebigmunch).',
    'long_description': '# tbm-utils.py\n\n[![PyPI](https://img.shields.io/pypi/v/tbm-utils.svg?label=PyPI)](https://pypi.org/project/tbm-utils/)\n![](https://img.shields.io/badge/Python-3.6%2B-blue.svg)  \n[![Travis](https://img.shields.io/travis/thebigmunch/tbm-utils.svg?label=Travis)](https://travis-ci.org/thebigmunch/tbm-utils)\n[![Codecov](https://img.shields.io/codecov/c/github/thebigmunch/tbm-utils.svg?label=Codecov)](https://codecov.io/gh/thebigmunch/tbm-utils)  \n[![Docs - Stable](https://img.shields.io/readthedocs/tbm-utils/stable.svg?label=Docs%20%28Stable%29)](https://tbm-utils.readthedocs.io/en/stable/)\n[![Docs - Latest](https://img.shields.io/readthedocs/tbm-utils/latest.svg?label=Docs%20%28Latest%29)](https://tbm-utils.readthedocs.io/en/latest/)\n\n[tbm-utils](https://github.com/thebigmunch/tbm-utils) is a commonly-used set of utilities used by me (thebigmunch).\n\n\n## Installation\n\n``pip install -U tbm-utils``\n\n\n## Usage\n\nFor the release version, see the [stable docs](https://tbm-utils.readthedocs.io/en/stable/).  \nFor the development version, see the [latest docs](https://tbm-utils.readthedocs.io/en/latest/).\n\n\n## Appreciation\n\nShowing appreciation is always welcome.\n\n#### Thank\n\n[![Say Thanks](https://img.shields.io/badge/thank-thebigmunch-blue.svg?style=flat-square)](https://saythanks.io/to/thebigmunch)\n\nGet your own thanks inbox at [SayThanks.io](https://saythanks.io/).\n\n#### Contribute\n\n[Contribute](https://github.com/thebigmunch/tbm-utils/blob/master/.github/CONTRIBUTING.md) by submitting bug reports, feature requests, or code.\n\n#### Help Others/Stay Informed\n\n[Discourse forum](https://forum.thebigmunch.me/)\n\n#### Referrals/Donations\n\n[![Digital Ocean](https://img.shields.io/badge/Digital_Ocean-referral-orange.svg?style=flat-square)](https://bit.ly/DigitalOcean-tbm-referral) [![Namecheap](https://img.shields.io/badge/Namecheap-referral-orange.svg?style=flat-square)](http://bit.ly/Namecheap-tbm-referral) [![PayPal](https://img.shields.io/badge/PayPal-donate-brightgreen.svg?style=flat-square)](https://bit.ly/PayPal-thebigmunch)\n',
    'author': 'thebigmunch',
    'author_email': 'mail@thebigmunch.me',
    'url': 'https://github.com/thebigmunch/tbm-utils',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
