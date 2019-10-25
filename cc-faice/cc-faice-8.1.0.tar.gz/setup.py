# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cc_faice',
 'cc_faice.agent',
 'cc_faice.agent.red',
 'cc_faice.commons',
 'cc_faice.convert',
 'cc_faice.convert.batches',
 'cc_faice.convert.cwl',
 'cc_faice.convert.format',
 'cc_faice.exec',
 'cc_faice.schema',
 'cc_faice.schema.list',
 'cc_faice.schema.show',
 'cc_faice.schema.validate']

package_data = \
{'': ['*']}

install_requires = \
['cc-core>=8.1,<8.2', 'keyring>=19.0,<20.0']

entry_points = \
{'console_scripts': ['faice = cc_faice.main:main']}

setup_kwargs = {
    'name': 'cc-faice',
    'version': '8.1.0',
    'description': 'FAICE (Fair Collaboration and Experiments) is part of the Curious Containers project. It enables researchers to perform and distribute reproducible data-driven experiments defined in the RED format.',
    'long_description': '# CC-FAICE\n\nFAICE (Fair Collaboration and Experiments) is part of the Curious Containers project and enables researchers to perform and distribute reproducible data-driven experiments defined in RED or CWL format.\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://www.curious-containers.cc/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
