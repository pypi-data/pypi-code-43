# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrnl', 'jrnl.plugins']

package_data = \
{'': ['*'], 'jrnl': ['templates/*']}

install_requires = \
['asteval>=0.9.14,<0.10.0',
 'cryptography>=2.7,<3.0',
 'keyring>=19.0,<20.0',
 'parsedatetime>=2.4,<3.0',
 'passlib>=1.7,<2.0',
 'python-dateutil>=2.8,<3.0',
 'pytz>=2019.1,<2020.0',
 'pyxdg>=0.26.0,<0.27.0',
 'pyyaml>=5.1,<6.0',
 'tzlocal>=1.5,<2.0']

extras_require = \
{':sys_platform == "win32"': ['colorama>=0.4.1,<0.5.0']}

entry_points = \
{'console_scripts': ['jrnl = jrnl.cli:run']}

setup_kwargs = {
    'name': 'jrnl',
    'version': '2.1b4',
    'description': 'Collect your thoughts and notes without leaving the command line.',
    'long_description': "jrnl [![Build Status](https://travis-ci.com/jrnl-org/jrnl.svg?branch=master)](https://travis-ci.com/jrnl-org/jrnl) [![Downloads](https://pepy.tech/badge/jrnl)](https://pepy.tech/project/jrnl) [![Version](http://img.shields.io/pypi/v/jrnl.svg?style=flat)](https://pypi.python.org/pypi/jrnl/)\n====\n\n_To get help, [submit an issue](https://github.com/jrnl-org/jrnl/issues/new) on Github._\n\n*jrnl* is a simple journal application for your command line. Journals are stored as human readable plain text files - you can put them into a Dropbox folder for instant syncing and you can be assured that your journal will still be readable in 2050, when all your fancy iPad journal applications will long be forgotten.\n\nOptionally, your journal can be encrypted using the [256-bit AES](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard).\n\n### Why keep a journal?\n\nJournals aren't just for people who have too much time on their summer vacation. A journal helps you to keep track of the things you get done and how you did them. Your imagination may be limitless, but your memory isn't. For personal use, make it a good habit to write at least 20 words a day. Just to reflect what made this day special, why you haven't wasted it. For professional use, consider a text-based journal to be the perfect complement to your GTD todo list - a documentation of what and how you've done it.\n\nIn a Nutshell\n-------------\n\nto make a new entry, just type\n\n    jrnl yesterday: Called in sick. Used the time to clean the house and spent 4h on writing my book.\n\nand hit return. `yesterday:` will be interpreted as a timestamp. Everything until the first sentence mark (`.?!`) will be interpreted as the title, the rest as the body. In your journal file, the result will look like this:\n\n    2012-03-29 09:00 Called in sick.\n    Used the time to clean the house and spent 4h on writing my book.\n\nIf you just call `jrnl`, you will be prompted to compose your entry - but you can also configure _jrnl_ to use your external editor.\n\nKnown Issues\n------------\njrnl used to support integration with Day One, but no longer supports it since Day One 2 was released with a different backend. [See the GitHub issue for more information](https://github.com/jrnl-org/jrnl/issues/409).\n\nAuthors\n-------\nCurrent maintainers:\n\n * Jonathan Wren ([wren](https://github.com/wren))\n * Micah Ellison ([micahellison](https://github.com/micahellison))\n\nOriginal maintainer:\n\n * Manuel Ebert ([maebert](https://github.com/maebert))\n",
    'author': 'Manuel Ebert',
    'author_email': 'manuel@1450.me',
    'url': 'https://jrnl.sh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
