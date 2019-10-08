# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jgt_common']

package_data = \
{'': ['*']}

install_requires = \
['requests', 'wrapt']

entry_points = \
{'console_scripts': ['uuid-replacer = jgt_common.uuid_replacer:main'],
 'tag_to_url': ['JIRA = jgt_common.tag_to_url:JIRA',
                'SNOW = jgt_common.tag_to_url:SNOW',
                'VersionOne = jgt_common.tag_to_url:VersionOne']}

setup_kwargs = {
    'name': 'jgt-common',
    'version': '1.0.2',
    'description': 'A library for helper functions across Jolly Good Toolbelt designed for larger consumption',
    'long_description': 'JGT Common Tools\n================\n\nA collection of tools that are shared\nacross multiple projects within Jolly Good Toolbelt\nbut useful to anyone.\n',
    'author': 'Doug Philips',
    'author_email': 'dgou@mac.com',
    'url': 'https://jolly-good-toolbelt.github.io/jgt_common/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
