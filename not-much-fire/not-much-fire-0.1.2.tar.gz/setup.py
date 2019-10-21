# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['not_much_fire']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'click>=7.0,<8.0',
 'dbus-python>=1.2,<2.0',
 'notify2>=0.3.1,<0.4.0',
 'notmuch>=0.29.1,<0.30.0']

entry_points = \
{'console_scripts': ['not-much-fire = not_much_fire.cli:main']}

setup_kwargs = {
    'name': 'not-much-fire',
    'version': '0.1.2',
    'description': 'A simple Notmuch notification tool',
    'long_description': '# Not Much Fire\n\nA simple [Notmuch](https://notmuchmail.org) notification tool\n\n- [Installation](#installation)\n- [Usage](#usage)\n- [Notmuch Hook](#notmuch-hook)\n\n## Installation\n\nInstall it globally with [pip](https://pip.pypa.io/en/stable):\n\n```shell\n$ pip install not-much-fire\n```\n\nExecute always the most recent version with [pipx](https://pipxproject.github.io/pipx/):\n\n```shell\n$ pipx run not-much-fire\n```\n\n## Usage\n\n```shell\n$ not-much-fire --help\n\nUsage: not-much-fire [OPTIONS]\n\n  A simple Notmuch notification tool.\n\n  Requests Notmuch for new unread messages and send notifications to the\n  desktop environment. Already notified messages get not shown again for a\n  whole day. If they remain unread, they get are handled again on the next\n  day.\n\nOptions:\n  --notmuch-query <query>  Used to query the unread messages from the Notmuch\n                          database  [default: is:unread and is:inbox]\n  --help                   Show this message and exit.\n```\n\n## Notmuch Hook\n\nTo get notification each time after `notmuch` has updated its database, add\na new hook. Therefore add a new line like the following into\n`$DATABASE/.notmuch/hooks/post-new`.\n\n```shell\n#!/bin/bash\nnot-much-fire\n# or: pipx run not-much-fire\n```\n\nCheckout `man notmuch-hooks` to get further information about hooks and\n`notmuch`. I recommend to set the `$NOTMUCH_CONFIG` environment variable to\nreach compatibility with the [XDG base directory\nstandard](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).\n',
    'author': 'Thore Weilbier',
    'author_email': 'thore@weilbier.net',
    'url': 'https://github.com/weilbith/not-much-fire',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
