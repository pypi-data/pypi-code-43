# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['red_connector_ssh', 'red_connector_ssh.convert_ssh_key']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.0,<4.0',
 'paramiko>=2.5,<3.0',
 'pexpect>=4.7.0,<5.0.0',
 'scp>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['red-connector-ssh = red_connector_ssh.main:main',
                     'red-convert-ssh-key = '
                     'red_connector_ssh.convert_ssh_key.main:main']}

setup_kwargs = {
    'name': 'red-connector-ssh',
    'version': '1.1',
    'description': 'RED Connector SSH is part of the Curious Containers project.',
    'long_description': '# RED Connector SSH\n\nRED Connector SSH is part of the Curious Containers project.\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://www.curious-containers.cc/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
