# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aiohypixel']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.5,<4.0', 'dataclasses>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'aiohypixel',
    'version': '0.2.0',
    'description': 'An asynchronous Hypixel API Wrapper written in Python',
    'long_description': "# aiohypixel \nA modern asynchronous Hypixel API wrapper with full API coverage written in Python.\n\n## Installation\n\nIt's very simple! Just use `pip`, like this: `pip install aiohypixel`.  \nIf you want to install the staging build, you can do so by running `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple aiohypixel` instead.\n\n## How do you use this?\n\nIf you like to read, you can check the documentation [**here**](https://tmpod.gitlab.io/aiohypixel)!\n\nIf not, here's a crash course:\n\n> **TODO**\n\n~~You can also check the `examples` folder for some more handsdown examples on how to use this library.~~ **TODO**\n\n## Ran into any issues?\n\nNo problem! Just head out to the [**Issues**](https://gitlab.com/Tmpod/aiohypixel/issues) and see if there's any opened or closed issue regarding situation. If not, feel free to open one!  \nYou can also join the support [**Matrix**](https://matrix.org) room at **`#aiohypixel:matrix.org`**.\n\n> :warning: This module is still under heavy development, and so there may occur major changes!\n\nKeep an eye on this page, as it will be updated when major progress is done :wink:\n\n",
    'author': 'Tmpod',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
