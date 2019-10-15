# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['freshchat', 'freshchat.client', 'freshchat.models', 'freshchat.webhook']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6,<4.0', 'cafeteria>=0.19,<0.20', 'pycrypto>=2.6,<3.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

setup_kwargs = {
    'name': 'freshchat',
    'version': '0.4.2',
    'description': 'A library provide a http client for Freshchat API',
    'long_description': '[![image](https://img.shields.io/pypi/v/freshchat.svg)](https://pypi.org/project/freshchat/)\n[![image](https://img.shields.io/pypi/l/freshchat.svg)](https://pypi.org/project/freshchat/)\n[![image](https://img.shields.io/pypi/pyversions/freshchat.svg)](https://pypi.org/project/freshchat/)\n[![image](https://readthedocs.org/projects/freshchat/badge/?version=latest&style=flat)](https://freshchat.readthedocs.io/)\n[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![](https://github.com/twyla-ai/python-freshchat/workflows/Main%20Workflow/badge.svg)](https://github.com/twyla-ai/python-freshchat/actions)\n[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=twyla-ai_python-freshchat&metric=alert_status)](https://sonarcloud.io/dashboard?id=com.lapots.breed.judge:judge-rule-engine)\n\n# Python Freshchat Client Library\nA python client library for [Freshchat (Live Chat Software)](https://www.freshworks.com/live-chat-software/). This library allows users to interact with the Freshchat API to perform actions on the following resources.\n\n* Users\n* Channels\n* Conversations\n\nThis library can also be used to build B2B or C2B live chat clients integrating with the Freshchat API.\n\n## Installation\n`pip install freshchat`\n\n## Documentation\nThe project documentation is available [here](https://freshchat.readthedocs.io/en/latest/). Be sure to check out the [introduction](https://freshchat.readthedocs.io/en/latest/intro.html) for usage examples.\n\n## Reporting Issues and Contributing\nThis project is maintained on [GitHub](https://github.com/twyla-ai/python-freshchat).\n',
    'author': 'Twyla Engineering',
    'author_email': 'software@twyla.ai',
    'url': 'https://github.com/twyla-ai/python-freshchat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
