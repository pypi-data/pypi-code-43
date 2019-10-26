# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['baretypes']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'baretypes',
    'version': '3.1.0',
    'description': 'Types for bareASGI and bareClient',
    'long_description': '# bareTypes\n\nTypes for bareASGI and bareClient\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/baretypes',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
