# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['feed2mail']

package_data = \
{'': ['*'], 'feed2mail': ['templates/*']}

install_requires = \
['Jinja2>=2.10,<3.0',
 'aiohttp>=3.6,<4.0',
 'aiosmtplib>=1.1,<2.0',
 'atoma>=0.0.17,<0.0.18']

entry_points = \
{'console_scripts': ['feed2mail = feed2mail:main']}

setup_kwargs = {
    'name': 'feed2mail',
    'version': '0.1.0',
    'description': 'Monitor a list of atom feeds and send an email digest with updates',
    'long_description': '# Feed2Mail\n\nMonitor a list of atom feeds and send an email digest with updates.\n\n## Installation\n`pip install feed2mail`\n\n## Config\n\nStore a JSON file containing a single object with keys of atom feed URLs and an empty value (or specify an ISO8601 timestamp to set the oldest time you care about). Specify it at runtime with `--config-path` (or `--config`). On a successful run, this file will be updated with new timestamps.\n```json\n{\n  "https://github.com/mattclement/feed2json/commits/master.atom": ""\n}\n```\n\nMail is sent via SMTP with STARTTLS. Use the program arguments (`--mail-<user|password|host|to>`) or environment variables (`FEED_MAIL_<USER|PASS|HOST|TO>`).\n',
    'author': 'Matt Clement',
    'author_email': 'm@nullroute.host',
    'url': 'https://github.com/mattclement/feed2mail',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
