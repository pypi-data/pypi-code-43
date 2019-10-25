# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['othelloai']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'othello-ai',
    'version': '0.1.0',
    'description': 'Othello game engine',
    'long_description': '# othello\nAn othello game engine\n\n## Dev environment\nFor the dev environment I recommend using [pyenv](https://github.com/pyenv/pyenv#installation) and [poetry](https://poetry.eustace.io/docs/#installation)\n1. Download and install \n1. Run `poetry install` \n1. Run `poetry run python -m othello`',
    'author': 'Jason R. Carrete',
    'author_email': 'jasoncarrete5@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jcarrete5/othello',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
