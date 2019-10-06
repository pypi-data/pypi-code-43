# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['raindrip', 'raindrip.metrics']

package_data = \
{'': ['*']}

install_requires = \
['kafka-python>=1.4,<2.0', 'psutil>=5.6,<6.0', 'psycopg2>=2.8,<3.0']

entry_points = \
{'console_scripts': ['raindrip = raindrip.cli:main']}

setup_kwargs = {
    'name': 'raindrip',
    'version': '0.0.1',
    'description': 'Collect various operating system metrics and stream it',
    'long_description': None,
    'author': 'Keshab Paudel',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
