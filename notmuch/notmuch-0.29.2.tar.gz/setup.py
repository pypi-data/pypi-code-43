# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['notmuch']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'notmuch',
    'version': '0.29.2',
    'description': 'Python binding of the notmuch mail search and indexing library.',
    'long_description': '# Notmuch Python Bindings\n\nPython binding of the notmuch mail search and indexing library. This module\nmakes the functionality of the notmuch library (`https://notmuchmail.org`\\_)\navailable to python. Successful import of this module depends on\na libnotmuch.so|dll being available on the user\'s system.\n\n## Installation\n\nThe intention of this repository is to make these bindings easily available for\ndependency management. It is originally taken from\n`https://git.notmuchmail.org/git/notmuch/bindings/python`.\n\n### PyPI\n\nInstall the build project from [PyPI](https://pypi.org/).\n\n```shell\n$ pip install notmuch\n```\n\n```shell\n$ poetry add notmuch\n```\n\n### Git\n\nReference the pure sources from\n[GitHub](https://github.com/weilbith/notmuch-python-bindings).\n\n```shell\npip install from git+https://github.com/weilbith/notmuch\n```\n\n```shell\npoetry add --git=https://github.com/weilbith/notmuch\n```\n\n---\n\n## Documentation\n\nIf you have downloaded the full source tarball, you can create the documentation\nwith sphinx installed, go to the docs directory and "make html". A static\nversion of the documentation is available at:\n\nhttps://notmuch.readthedocs.io/projects/notmuch-python/\n',
    'author': 'Sebastian Spaeth',
    'author_email': 'Sebastian@SSpaeth.de',
    'url': 'https://github.com/weilbith/notmuch-bindings.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
