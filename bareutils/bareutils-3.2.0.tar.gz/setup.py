# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['bareutils', 'bareutils.compression']

package_data = \
{'': ['*']}

install_requires = \
['baretypes>=3.1.0,<4.0.0']

setup_kwargs = {
    'name': 'bareutils',
    'version': '3.2.0',
    'description': 'Utilities for bareASGI and bareClient',
    'long_description': '# bareutils\nUtilities for bareASGI and bareClient\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/bareutils',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
