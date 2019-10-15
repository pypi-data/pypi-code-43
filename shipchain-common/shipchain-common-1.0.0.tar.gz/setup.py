# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['shipchain_common', 'shipchain_common.custom_logging']

package_data = \
{'': ['*']}

install_requires = \
['aws-requests-auth>=0.4,<0.5',
 'boto3>=1.9,<1.10',
 'cryptography>=2.5,<2.6',
 'django-enumfields>=0.10.0,<0.11.0',
 'django-influxdb-tagged-metrics==1.3.3',
 'django>=2.2.4,<3.0.0',
 'djangorestframework-jsonapi>=2.5,<2.6',
 'djangorestframework>=3.9.1,<4.0.0',
 'python-dateutil>=2.7.5,<2.8.0',
 'requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'shipchain-common',
    'version': '1.0.0',
    'description': "A PyPI package containing shared code for ShipChain's Python/Django projects.",
    'long_description': "# python-common\nA PyPI package containing shared code for ShipChain's Python/Django projects\n",
    'author': 'Adam Hodges',
    'author_email': 'ahodges@shipchain.io',
    'url': 'https://github.com/ShipChain/python-common',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
