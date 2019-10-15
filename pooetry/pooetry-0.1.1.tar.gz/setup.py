# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pooetry']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pooetry = pooetry:main.main']}

setup_kwargs = {
    'name': 'pooetry',
    'version': '0.1.1',
    'description': 'An almost-useless wrapper for the great packaging tool poetry',
    'long_description': "# What is this?\n`pooetry` is a python wrapper utility with a very narrow use case.  If you don't know what it does you probably don't need it 🙃\n\n# What does it do?\nThis utility automagically fixes issues caused by these factors combined:\n* `poetry 0.12.*`\n* `pip 19.*`\n* Use a private package repo which requires authentication\n* Have special characters in your credentials for this private repo\n    * _commonly caused by having an email as a username (the '@' is not URL legal)_\n\nIf you are stuck in this situation you'll find yourself changing the credentials between quoted and non-quoted as _some_ `poetry` commands only work with quoted creds while _others_ only work with non-quoted creds.\n\n# How do I use it?\n1. Install `poetry`\n    * Best to follow the [install procedure on the official `poetry` repo](https://github.com/sdispater/poetry#installation)\n2. Install `pooetry`\n    * You can use the package manager of your choice for this, `pip install pooetry` for example\n3. When you want to run `poetry` simply use `pooetry` instead.  All the commands and options will be passed through.",
    'author': 'ChrisArgyle',
    'author_email': 'chrisisdiy@gmail.com',
    'url': 'https://github.com/ChrisArgyle/pooetry',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
