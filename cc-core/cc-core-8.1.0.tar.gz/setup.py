# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cc_core',
 'cc_core.agent',
 'cc_core.commons',
 'cc_core.commons.schemas',
 'cc_core.commons.schemas.engines']

package_data = \
{'': ['*'], 'cc_core.agent': ['blue/*']}

install_requires = \
['docker>=4.0,<5.0', 'jsonschema>=3.1,<4.0', 'ruamel.yaml>=0.16.5,<0.17.0']

setup_kwargs = {
    'name': 'cc-core',
    'version': '8.1.0',
    'description': 'CC-Core is part of the Curious Containers project. It contains shared code of the CC-FAICE and CC-Agency packages.',
    'long_description': '# CC-Core\n\nCC-Core is part of the Curious Containers project. It provides common functionality for other parts of Curious Containers and implements agents to run data-driven experiments defined in RED or CWL format.\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://www.curious-containers.cc/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
