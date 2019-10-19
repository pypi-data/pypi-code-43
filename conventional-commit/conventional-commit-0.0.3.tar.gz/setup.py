# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gitcommit']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['gitcommit = gitcommit.gitcommit:main']}

setup_kwargs = {
    'name': 'conventional-commit',
    'version': '0.0.3',
    'description': 'a tool for writing conventional commits, conveniently',
    'long_description': '<p  align="center">\n  <strong>gitcommit</strong>\n  <br>\n  <code>a tool for writing conventional commits, conveniently</code>\n  <br><br>\n  <a href="https://badge.fury.io/py/conventional-commit"><img src="https://badge.fury.io/py/conventional-commit.svg" alt="PyPI version" height="18"></a>\n</p>\n\n# Install\n\nTo install\n\n```\npip install conventional-commit\n```\n\nTo use, run the following command from within a git repository\n\n```\ngitcommit\n```\n\n# Overview\n\nThe purpose of this utility is to expedite the process of committing with a conventional message format in a user friendly way. This tool is not templated, because it sticks rigidly to the [Conventional Commit standard](https://www.conventionalcommits.org), and thus not designed to be \'altered\' on a case by case basis.\n\nCommit messages produced follow the general template:\n```\n<type>[(optional scope)]: <description>\n\n[BREAKING CHANGE: ][optional body / required if breaking change]\n\n[optional footer]\n```\n\nAdditional rules implemeted:\n\n1. Subject line (i.e. top) should be no more than 50 characters.\n2. Every other line should be no more than 72 characters.\n3. Wrapping is allowed in the body and footer, NOT in the subject.\n\n# Development\n\nFor development, see the developer readme file: [README.dev.md](./README.dev.md)\n',
    'author': 'nebbles',
    'author_email': None,
    'url': 'https://github.com/nebbles/gitcommit',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
