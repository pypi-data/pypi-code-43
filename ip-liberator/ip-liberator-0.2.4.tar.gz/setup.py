# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ip_liberator']

package_data = \
{'': ['*']}

install_requires = \
['boto3==1.9.133']

entry_points = \
{'console_scripts': ['ip-liberator = ip_liberator.__main__:main']}

setup_kwargs = {
    'name': 'ip-liberator',
    'version': '0.2.4',
    'description': 'A command line utility to update AWS Security Groups rules.',
    'long_description': '============\nIP Liberator\n============\n\n\n.. image:: https://img.shields.io/pypi/v/ip-liberator.svg\n        :target: https://pypi.python.org/pypi/ip-liberator\n\n.. image:: https://img.shields.io/travis/wagnerluis1982/ip-liberator.svg\n        :target: https://travis-ci.org/wagnerluis1982/ip-liberator\n\n.. image:: https://readthedocs.org/projects/ip-liberator/badge/?version=latest\n        :target: https://ip-liberator.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n\nA command line utility to update AWS Security Groups rules.\n\n\n* Free software: GNU General Public License v3\n* Documentation: https://ip-liberator.readthedocs.io.\n\n\nFeatures\n--------\n\n* Update a list of security groups of your AWS account at once.\n* Grant access to informed ports for your current IP address or an informed IP.\n* Read profile files in JSON with all the information needed to contact.\n* Fit for use as script (e.g. to update your dynamic IP regularly).\n\nInstallation\n------------\n\n.. code-block:: console\n\n    $ pip install ip-liberator\n\nQuickstart\n----------\n\nConsider a file ``/path/my-profile.json`` with the following content:\n\n.. code-block:: json\n\n    {\n      "credentials": {\n        "access_key": "<AWS_ACCESS_KEY>",\n        "secret_key": "<AWS_SECRET_KEY>",\n        "region_name": "<AWS REGION>"\n      },\n      "config": {\n        "operator": "John",\n        "services": [\n          {\n            "name": "FTP+SFTP",\n            "port": "21-22"\n          },\n          {\n            "name": "HTTPS",\n            "port": "443"\n          }\n        ],\n        "security_groups": [\n          "sg-<GROUP_ID_1>",\n          "sg-<GROUP_ID_2>"\n        ]\n      }\n    }\n\nUsing the profile defined above will create or update two entries in the informed security groups:\n\n- **John FTP+SFTP** granting access for the current IP the ports 21 and 22.\n- **John HTTPS** granting access for the current IP the port 443.\n\nTo accomplish it, simply run:\n\n.. code-block:: console\n\n    $ ip-liberator --profile /path/my-profile.json\n    Authorizing rules [\'John FTP+SSH\', \'John HTTPS\'] to IP 192.30.253.112/32\n    - sg-<GROUP_ID_1>\n    - sg-<GROUP_ID_2>\n\nCredits\n-------\n\nAuthors\n:::::::\n\n* Wagner Macedo <wagnerluis1982@gmail.com> (maintainer)\n\n\n=======\nHistory\n=======\n\nAll notable changes to this project will be documented in this file.\n\nThe format is based on `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_,\nand this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.\n\n0.2.4 (2019-10-10)\n------------------\n\nAdded\n+++++\n\n- Improve script output showing version and a cool summary of settings.\n\nFixed\n+++++\n\n- When using a tag, the script was always reauthorizing even when IP was not changed,\n  this version fixed this bad behavior.\n\n0.2.3 (2019-09-20)\n------------------\n\nFixed\n+++++\n\n- Fix tagged rule is retagged when authorizing or revoking\n\n0.2.2 (2019-09-18)\n------------------\n\nThis release marks a breaking change. Now the script "tags" recorded entries in\nthe security groups, e.g. ``[ip-liberator] SSH John`` instead of only ``SSH John``.\nThat helps to identify what IP Liberator added and what was added by hand.\n\nBy default, the tag is **ip-liberator**, but can be change through the new\noption ``--tag``. If the user wants the previous behavior, i.e. without a tag,\nhe or she must pass the option ``--no-tag``.\n\nAdded\n+++++\n\n- Add option ``--operator`` to change the profile operator.\n- Add short option ``-p`` for ``--profile``\n- Add option ``--version`` to show current script version.\n\nChanged\n+++++++\n\n- Add option ``--tag`` to identify entries added by the script.\n- Migrate build system to Poetry\n\n0.2.1 (2019-04-19)\n------------------\n\n- Fix documentation\n\n0.2.0 (2019-04-19)\n------------------\n\nThis release marks as the first to be published to PyPI.\n\nNo new functionality was added. The version was changed was to place a history mark.\n\n- Added documentation.\n- Added full coverage tests.\n- Code refactoring.\n\n0.1.1 (2018-10-16)\n------------------\n\n- Better console output.\n- Added option ``--revoke-only``.\n- Don\'t reauthorize if the IP address is already in the security group.\n- Authorizing and revoking in batch to be more efficient.\n- Bugfixes\n\n0.1.0 (2018-09-27)\n------------------\n\n- Added option ``--my-ip`` to inform an IP address explicitly.\n- Show in console the security groups being processed.\n- Allow use as script by reading JSON as external config.\n',
    'author': 'Wagner Macedo',
    'author_email': 'wagnerluis1982@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wagnerluis1982/ip-liberator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
