# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['privibot']

package_data = \
{'': ['*']}

install_requires = \
['python-telegram-bot==12.0.0b1', 'sqlalchemy>=1.3,<2.0']

entry_points = \
{'console_scripts': ['privilegebot = privilegebot.cli:main']}

setup_kwargs = {
    'name': 'privibot',
    'version': '0.1.0',
    'description': 'A library to build Telegram Bot with a privilege system.',
    'long_description': '# privibot\nThis library provides decorators to restrict access to your Telegram bot handlers based on privileges given to users.\nThe privileges are stored in a database through SQLAlchemy (SQLite, Postgres, etc.).\n\n## Installation\n\n```\npip install privibot\n```\n\n## Usage\nTo restrict access to a handler, decorate your callback functions like following:\n\n```python\nfrom privibot import require_access, require_admin\n\n\n@require_access\ndef callback_for_registered_users(update, context):\n    pass\n  \n  \n@require_admin\ndef callback_for_admins_only(update, context):\n    pass\n```\n\nTo use custom privileges, define them like so:\n\n```python\n# privileges.py\nfrom privibot import Privilege, Privileges as Ps\n\n\nclass Privileges(Ps):\n    MEDIA_MANAGER = Privilege(\n        name="media_manager",\n        verbose_name="Media Manager",\n        description="This privilege allows users to act (accept or reject) on media-related requests.",\n    )\n    USER_MANAGER = Privilege(\n        "user_manager", "User Manager", "This privilege allows users to manage access of other users to the bot."\n    )\n    TESTER = Privilege("tester", "Tester", "This privilege allows users to test new things.")\n```\n\nNow simply use these privileges with the decorator:\n\n```python\nfrom privibot import require_privileges\n\nfrom .privileges import Privileges\n\n\n@require_privileges([Privileges.USER_MANAGER])\ndef callback_for_user_managers_only(update, context):\n    pass\n```\n\nYou can also manually check for privileges like so:\n\n```python\nfrom privibot import User\n\nfrom .privileges import Privileges\n\n\ndef some_callback(update, context):\n    telegram_user = update.effective_user\n    db_user = User.get_with_id(telegram_user.id)\n    \n    if db_user.has_privilege(Privileges.TESTER):\n        # do something\n    elif db_user.has_privileges([Privileges.MEDIA_MANAGER, Privileges.USER_MANAGER]):\n        # do something else\n```\n\nUsers who do not pass the privilege test will receive a message saying they have been denied access.\n\n## Built-in handlers\nThis library also provides handlers and their callbacks for the following commands:\n- /start\n- /help\n- /requestAccess\n- /myPrivileges\n- /grant\n- /revoke\n\n\n',
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'url': 'https://github.com/pawamoy/privibot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
