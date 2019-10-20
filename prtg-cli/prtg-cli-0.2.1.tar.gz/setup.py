# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['prtg_cli', 'prtg_cli.commands', 'prtg_cli.core']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'jsonschema>=3.1,<4.0',
 'pyyaml>=5.1,<6.0',
 'requests>=2.22,<3.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['prtg-cli = prtg_cli.cli:main']}

setup_kwargs = {
    'name': 'prtg-cli',
    'version': '0.2.1',
    'description': 'CLI for PRTG Network Monitor',
    'long_description': "# prtg-cli [![PyPi version](https://img.shields.io/pypi/v/prtg-cli.svg)](https://pypi.python.org/pypi/prtg-cli/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/prtg-cli.svg)](https://pypi.python.org/pypi/prtg-cli/) [![](https://img.shields.io/github/license/f9n/prtg-cli.svg)](https://github.com/f9n/prtg-cli/blob/master/LICENSE)\n\nCLI for PRTG Network Monitor\n\n# Installation\n\n```bash\n$ pip3 install --user --upgrade prtg-cli\n```\n\n# Setup\n\nFor communication with PRTG, use options or set the `PRTG_HOST`, `PRTG_USERNAME`, (`PRTG_PASSWORD` or `PRTG_PASSHASH`) environment variables\n\n# Usage\n\n```bash\n$ prtg-cli\nUsage: prtg-cli [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --host TEXT      Host of the PRTG\n  --username TEXT  Username of the PRTG\n  --password TEXT  Password of the PRTG\n  --passhash TEXT  Passhash of the PRTG\n  --help           Show this message and exit.\n\nCommands:\n  duplicate\n  get\n  object\n  passhash\n  prtg_version\n  sensor_types\n  status\n  version\n```\n\n# Suggestions\n\n- Please use a unique name for `probes`, `groups` and `devices` on PRTG\n\n# Examples\n\n### Information\n```bash\n### Get all probes\n$ prtg-cli get probes\n### Get all groups \n$ prtg-cli get groups\n### Get specific group\n$ prtg-cli get groups <GROUP_NAME>\n### Get all devices\n$ prtg-cli get devices\n### Get specific device\n$ prtg-cli get devices <DEVICE_NAME>\n```\n\n### Duplication\n```bash\n### Duplicate a group\n$ prtg-cli duplicate group --source <Source_Group> --target <Target_Group> --target-name <New_Group_Name>\n### Duplicate a device\n$ prtg-cli duplicate device --source <Source_Device> --target-group <Target_Group> --target-name <New_Device_Name> --target-host <New_Device_Host>\n```\n\n### Object Manipulation\n```bash\n### Scan a object\n$ prtg-cli object --state scan --resource devices --item <DEVICE_NAME>\n### Resume a object\n$ prtg-cli object --state resume --resource devices --item <DEVICE_NAME>\n### Stop a object\n$ prtg-cli object --state stop --resource devices --item <DEVICE_NAME>\n### Delete a object\n$ prtg-cli object --state delete --resource devices --item <DEVICE_NAME>\n```\n\n# Example of Adding Multiple Devices With Config File\n\n```bash\n$ cat example.yml\n# Device Name\nclone: PROD_RABBITMQ_CLUSTER\n# Target Group\ngroup: PRTG_CLI\n\ndevices:\n  - name: CHECKOUT_RMQ_CLUSTER_01\n    host: 10.0.20.32\n\n  - name: CHECKOUT_RMQ_CLUSTER_02\n    host: 10.0.20.33\n\n$ prtg-cli manager --config-file example.yml\n- Create new 'CHECKOUT_RMQ_CLUSTER_01' device\n- Create new 'CHECKOUT_RMQ_CLUSTER_02' device\n```\n\n# Credits\n\nThank you for offering fabulous, amazing, incredible rest api at PRTG, it is very nice. :)\n\nhttps://www.paessler.com/prtg\n",
    'author': 'Fatih Sarhan',
    'author_email': 'f9n@protonmail.com',
    'url': 'https://github.com/f9n/prtg-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
