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
    'version': '0.0.1',
    'description': 'An asynchronous Hypixel API Wrapper written in Python',
    'long_description': "# `aiohypixel` - An asynchronous Hypixel API Wrapper written in Python\n\nThis module is still being made, but how will it work?\n- The base for every operation is going to be a session. Through it you'll be able to make every request you want (player or guild stuff).\n- Then there will be dataclasses for each type of request (player or guild). In the case of player requests there will actually be two dataclasses. \n    - One for a full player model (all those random bits of info + stats) and a partial player model (just the random info without the stats). You'll also be able to request just the stats.\n    - The stats will also be dataclasses, with each main gamemode having a specific dataclass and the less played ones just using the base one (at least for the first releases)\n- For guild stuff there will be just a dataclass that hold everything as it's usually a smaller data piece.\n\nIt should be noted that this can (and will probably) change in the future.\n\nKeep an eye on this page, as it will be updated when major progress is done :wink:\n\n",
    'author': 'Tmpod',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
