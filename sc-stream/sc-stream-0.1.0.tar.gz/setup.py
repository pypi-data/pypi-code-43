# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['sc_stream']

package_data = \
{'': ['*']}

install_requires = \
['kafka-python>=1.4,<2.0']

setup_kwargs = {
    'name': 'sc-stream',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': '仇昌栋',
    'author_email': 'qiuchangdong@cmhi.chinamobile.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
