# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['pawabot']

package_data = \
{'': ['*']}

install_requires = \
['aria2p>=0.6.0,<0.7.0',
 'beautifulsoup4>=4.8,<5.0',
 'loguru>=0.3.2,<0.4.0',
 'privibot>=0.1.0,<0.2.0',
 'python-telegram-bot==12.0.0b1',
 'requests>=2.22,<3.0',
 'sqlalchemy>=1.3,<2.0',
 'tomlkit>=0.5.5,<0.6.0',
 'xdg>=4.0,<5.0']

entry_points = \
{'console_scripts': ['pawabot = pawabot.cli:main']}

setup_kwargs = {
    'name': 'pawabot',
    'version': '0.1.1',
    'description': 'A bot for many things: aria2 management, torrent sites crawling, media organization with filebot and plex.',
    'long_description': '<!--\nIMPORTANT:\n  This file is generated from the template at \'scripts/templates/README.md\'.\n  Please update the template instead of this file.\n-->\n\n# pawabot\n<!--\n[![pipeline status](https://gitlab.com/pawamoy/pawabot/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/pawabot/pipelines)\n[![coverage report](https://gitlab.com/pawamoy/pawabot/badges/master/coverage.svg)](https://gitlab.com/pawamoy/pawabot/commits/master)\n[![documentation](https://img.shields.io/readthedocs/pawabot.svg?style=flat)](https://pawabot.readthedocs.io/en/latest/index.html)\n[![pypi version](https://img.shields.io/pypi/v/pawabot.svg)](https://pypi.org/project/pawabot/)\n-->\n\nA bot for many things: aria2 management, torrent sites crawling, media organization with filebot and plex.\n\nThis bot provides a command to search for torrents on the web, and let you select them for download.\nThere is a basic permission system allowing to manage multiple users for one bot.\n\n## Requirements\npawabot requires Python 3.6 or above.\n\n<details>\n<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.6\npyenv install 3.6.8\n\n# make it available globally\npyenv global system 3.6.8\n```\n</details>\n\n## Installation\nWith `pip`:\n```bash\npython3.6 -m pip install pawabot\n```\n\nWith [`pipx`](https://github.com/cs01/pipx):\n```bash\n# install pipx with the recommended method\ncurl https://raw.githubusercontent.com/cs01/pipx/master/get-pipx.py | python3\n\npipx install --python python3.6 pawabot\n```\n\n## Setup\n1. Create your Telegram bot account by talking to the `@godfather` bot.\n2. Write your bot token in `~/.config/pawabot/bot_token.txt`,\n   or set and export the environment variable `BOT_TOKEN`.\n3. Register your Telegram main account as administrator in the database with:\n```\npawabot create-admin -i MY_TG_ID -u MY_TG_USERNAME\n```\n\n## Usage\n```\nusage: pawabot [-h] [-L {TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL}]\n               ...\n\noptional arguments:\n  -h, --help            show this help message and exit\n\nCommands:\n  \n    run                 Run the bot.\n    create-admin        Create an administrator in the database.\n    create-user         Create a user in the database.\n    list-users          List registered users.\n\nGlobal options:\n  -L {TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL}, --log-level {TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL}\n                        Log level to use\n\n```\n\nCommands:\n\n- [`create-admin`](#create-admin)\n- [`create-user`](#create-user)\n- [`list-users`](#list-users)\n- [`run`](#run)\n\n\n### `create-admin`\n```\nusage: pawabot create-admin [-h] [-i UID] [-u USERNAME]\n\nCreate an administrator in the database.\n\noptional arguments:\n  -h, --help            Show this help message and exit.\n  -i UID, --uid UID     Telegram user id.\n  -u USERNAME, --username USERNAME\n                        Telegram user name.\n\n```\n\n\n\n### `create-user`\n```\nusage: pawabot create-user [-h] [-i UID] [-u USERNAME] [-a]\n\nCreate a user in the database.\n\noptional arguments:\n  -h, --help            Show this help message and exit.\n  -i UID, --uid UID     Telegram user id.\n  -u USERNAME, --username USERNAME\n                        Telegram user name.\n  -a, --admin           Give admin access.\n\n```\n\n\n\n### `list-users`\n```\nusage: pawabot list-users [-h]\n\nList registered users.\n\noptional arguments:\n  -h, --help  Show this help message and exit.\n\n```\n\n\n\n### `run`\n```\nusage: pawabot run [-h]\n\nRun the bot.\n\noptional arguments:\n  -h, --help  Show this help message and exit.\n\n```\n\n\n\n\n## Screenshots\n/start | /help | /search\n------ | ----- | -------\n![start](img/start.jpg) | ![help](img/help.jpg) | ![search](img/search.jpg)\n',
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'url': 'https://github.com/pawamoy/pawabot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
