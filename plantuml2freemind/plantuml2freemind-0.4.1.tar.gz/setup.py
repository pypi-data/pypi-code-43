# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plantuml2freemind']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0,<20.0.0']

entry_points = \
{'console_scripts': ['plantuml2freemind = plantuml2freemind.cli:main']}

setup_kwargs = {
    'name': 'plantuml2freemind',
    'version': '0.4.1',
    'description': 'Converts plantuml mindmaps to freemind .mm files',
    'long_description': "# plantuml2freemind\n\n\nConverts plantuml mindmaps to FreeMind .mm files.\n\nCreated especially for [Teamlead Roadmap](https://github.com/tlbootcamp/tlroadmap) project, which stores and\nmaintains a big community-driven roadmap in a mindmap. It's very convenient to have text plantuml as a source\nformat and generate other required formats from it.\n\n## Prerequisites\n\n- python >= 3.7 \n\n## Installation\n\n`pip install plantuml2freemind`\n\n## Usage\n\n`plantuml2freemind --help`\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)",
    'author': 'Boger',
    'author_email': 'kotvberloge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/b0g3r/plantuml2freemind',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
