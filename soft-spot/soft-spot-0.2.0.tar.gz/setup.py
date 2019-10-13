# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['soft_spot']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['sspot = soft_spot.__main__:cli']}

setup_kwargs = {
    'name': 'soft-spot',
    'version': '0.2.0',
    'description': 'Move to a land of Spot AWS instances',
    'long_description': '# soft-spot\n\n[![Build Status](https://dev.azure.com/messier-16/soft-spot/_apis/build/status/fferegrino.soft-spot?branchName=master)](https://dev.azure.com/messier-16/soft-spot/_build/latest?definitionId=1&branchName=master) [![PyPI version](https://badge.fury.io/py/soft-spot.svg)](https://pypi.org/project/soft-spot/)\n\nDo you have a soft spot for cheap cloud computing (**a.k.a. AWS Spot instances**)? Me too, no shame on that.\n\nHowever, what is a shame is having to go through that clunky UI and click here and there to get one; `soft-spot` makes it dead easy to launch an instance:\n\n## How?\nJust define a file with the specifications of the machine you want to launch:  \n\n```ini\n[INSTANCE]\nami = ami-06f2f779464715dc5\ntype = t2.micro\nsecurity_group = wizard-launch\nkey_pair = a_secret_key\nspot_price = 0.0035\n\n[ACCOUNT]\nuser = unbuntu\n\n[VOLUME]\nid = vol-volume123\ndevice = /dev/sda2\nmount_point = /data/\n```\n\nThen just execute the `sspot request` command:  \n\n```bash\nsspot request <<instance_config_file>>\n```\n\n### Credentials  \nThis script uses `boto3` so I strongly recommend heading over to [its documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to learn more.  \n\nAlternatively, you could create a tiny configuration file like this:  \n\n```ini\n[DEFAULT]\naws_access_key_id = an_acces_key\naws_secret_access_key = a_secret_key\nregion_name = us-west-1\n```\n\nAnd then pass it on to the `spot` command:\n\n```bash\nsspot -a ~/aws_credentials.txt request <<instance_config_file>> \n```\n',
    'author': 'Antonio Feregrino',
    'author_email': 'antonio.feregrino@gmail.com',
    'url': 'https://github.com/fferegrino/soft-spot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
