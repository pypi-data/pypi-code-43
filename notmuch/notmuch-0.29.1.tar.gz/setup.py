# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['notmuch']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'notmuch',
    'version': '0.29.1',
    'description': 'Python binding of the notmuch mail search and indexing library.',
    'long_description': None,
    'author': 'Sebastian Spaeth',
    'author_email': 'Sebastian@SSpaeth.de',
    'url': 'https://github.com/weilbith/notmuch-bindings.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
