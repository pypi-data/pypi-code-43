# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['google-stubs']

package_data = \
{'': ['*'],
 'google-stubs': ['api/*',
                  'logging/*',
                  'logging/type/*',
                  'longrunning/*',
                  'rpc/*',
                  'type/*']}

install_requires = \
['googleapis-common-protos>=1.6,<2.0',
 'typing-extensions>=3.7,<4.0',
 'typing>=3.7,<4.0']

setup_kwargs = {
    'name': 'googleapis-common-protos-stubs',
    'version': '1.0.0',
    'description': 'Type stubs for googleapis-common-protos',
    'long_description': '# Type stubs for googleapis-common-protos\nThis package provides type stubs for the [googleapis-common-protos](https://pypi.org/project/googleapis-common-protos/) package.\n\n**This is in no way affiliated with Google.**\n\nThe annotations were created automatically by [mypy-protobuf](https://github.com/dropbox/mypy-protobuf).\n\n## Installation\n```shell script\n$ pip install googleapis-common-protos-stubs\n```\n',
    'author': 'Henrik Bruåsdal',
    'author_email': 'henrik.bruasdal@gmail.com',
    'url': 'https://github.com/henribru/googleapis-common-protos-stubs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
