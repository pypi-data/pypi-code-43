# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mastools', 'mastools.models']

package_data = \
{'': ['*'], 'mastools': ['scripts/*']}

install_requires = \
['psycopg2>=2.8,<3.0', 'sqlalchemy>=1.3,<2.0']

entry_points = \
{'console_scripts': ['mastools = '
                     'mastools.scripts.cmd_mastools:handle_command_line',
                     'show-user-changes = '
                     'mastools.scripts.show_user_changes:handle_command_line']}

setup_kwargs = {
    'name': 'mastools',
    'version': '0.2.0',
    'description': "Tools for interacting directly with a Mastodon instance's database",
    'long_description': '# mastools - Tools for interacting directly with a Mastodon instance\'s database\n\n## Installation\n\nIf you just want to use mastools and not work on the project itself: `pip install mastools`.\n\nIf you want to help develop mastools and have [poetry](https://poetry.eustace.io) installed, clone this repo and run `poetry install`.\n\nIf you want to develop mastools but don\'t have poetry, use `pip` to install the dependencies mentioned in the `[tool.poetry.dependencies]` section of `pyproject.toml`.\n\n## Configuration\n\nMake a file named `~/.mastools/config.json` like:\n\n```json\n{\n    "host": "localhost",\n    "database": "mastodon",\n    "user": "mastodon",\n    "password": "0xdeadbeef"\n}\n```\n\nAll mastools components will use this database configuration.\n\n# The tool\n\nStarting with version 0.2.0, there\'s only one main `mastools` command which has\nmultiple subcommands. `show-user-changes` is still a functioning command for\ntemporary backward compatibility, but it will be removed soon.\n\n`mastools` subcommands:\n\n## show-unconfirmed-users\n\nShow users who haven\'t confirmed their email yet, ordered by their creation date\nfrom oldest to newest.\n\nThis is useful for detection a flood of newly created junk accounts.\n\n```\n$ mastools show-unconfired-users\ncrqcrujofa <cfvzm@example.com> was created at 2019-10-25 10:10:18.406158\nlkjmadf <ljchrew@example.com> was created at 2019-10-25 13:06:04.175580\n```\n\n## show-user-changes\n\nShow any new, changed, or deleted accounts that mention URLs in their account\ninfo.\n\nThis is super common for spammers, who like to stuff their crummy website\'s info\ninto every single field possible. Suppose you run this hourly and email yourself\nthe results (which will usually be empty unless your instance is *very* busy).\nNow you can catch those "https://support-foo-corp/" spammers before they have a\nchance to post!\n\nFor example I run this from a cron job on my instance like:\n\n```\n10 * * * * /home/me/mastools/.venv/bin/mastools show-user-changes\n```\n\nto get an hourly update of changes. This gives a report like:\n\n```\nChanged user: tek\n fields:\n  - \'Avatar\': \'Me, at night, with tunes\'\n    \'Website\': \'https://honeypot.net\'\n  + \'Avatar\': \'Me, at night, with music\'\n note:\n  <unchanged>\n\nNew user: new_spammer\n fields:\n  + \'website\': \'https://example.com/foo-corp-tech-support\'\n note:\n  + \'ALL UR FRAUD^WSUPPORT NEEDS\'\n\nDeleted user: old_spammer\n fields:\n  - \'website\': \'https://example.com/bar-inc-tech-support\'\n note:\n  - \'SEND ME YOUR IP ADDRESS AND CREDIT CARD\'\n```\n\n# License\n\nDistributed under the terms of the MIT license, mastools is free and open source software.\n\n# History\n\n- v0.2.0 - 2019-10-27: Added `mastools` command and `show_unconfirmed_users` subcommand\n- v0.1.3 - 2019-09-25: Productionizing\n- v0.1.2 - 2019-09-25: Prettier show-user-changes output\n- v0.1.1 - 2019-09-24: Same code, but pushing new metadata to pypi\n- v0.1.0 - 2019-09-24: First release\n',
    'author': 'Kirk Strauser',
    'author_email': 'kirk@strauser.com',
    'url': 'https://github.com/freeradical-dot-zone/mastools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
