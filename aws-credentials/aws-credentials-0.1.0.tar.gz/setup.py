# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['aws_credentials']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['aws-credentials = aws_credentials:cli']}

setup_kwargs = {
    'name': 'aws-credentials',
    'version': '0.1.0',
    'description': 'AWS credential manager',
    'long_description': '# AWS Credentials\n\nThis tool lets you easily manage AWS IAM Credentials for a user.\n',
    'author': 'Paul Robertson',
    'author_email': 't.paulrobertson@gmail.com',
    'url': 'https://gitlab.com/perobertson/aws-credentials',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
