# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['preacher',
 'preacher.app',
 'preacher.app.cli',
 'preacher.app.listener',
 'preacher.compilation',
 'preacher.core']

package_data = \
{'': ['*'], 'preacher': ['resources/html/*', 'resources/html/macros/*']}

install_requires = \
['aniso8601>=8.0,<9.0',
 'jinja2>=2.10,<3.0',
 'lxml>=4.4,<5.0',
 'pyhamcrest>=1.9,<2.0',
 'pyjq>=2.3,<3.0',
 'requests>=2.21,<3.0',
 'ruamel.yaml>=0.15.89,<0.16.0']

entry_points = \
{'console_scripts': ['preacher-cli = preacher.app.cli.main:main']}

setup_kwargs = {
    'name': 'preacher',
    'version': '0.11.4',
    'description': 'A web API verification tool.',
    'long_description': '# Preacher: Web API Verification Valuing Automation and Reality\n\n[![PyPI version](https://badge.fury.io/py/preacher.svg)][PyPI]\n[![Documentation Status](https://readthedocs.org/projects/preacher/badge/?version=latest)][Read the Docs]\n[![CircleCI](https://circleci.com/gh/ymoch/preacher.svg?style=svg)][Circle CI]\n[![Codecov](https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg)][Codecov]\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg?logo=lgtm&logoWidth=18)][LGTM]\n\nPreacher verifies API servers,\nwhich requests to the servers and verify the responses along to given scenarios.\n\nScenarios are written in [YAML][], bodies are analyzed [jq][] or [XPath][] queries\nand validation rules are based on [Hamcrest][] ([PyHamcrest][])\nso that any developers can write without learning toughly.\n\nThe full documentation is available at [preacher.readthedocs.io][Read the Docs].\n\n## Targets\n\n- Flexible validation to test with real backends: neither mocks nor sandboxes.\n  - Matcher-based validation.\n- CI Friendly to automate easily.\n  - A CLI application and YAML-based scenarios.\n\n## Usage\n\nFirst, install Preacher.\n\nThe most basic way to install Preacher is using `pip`. Supports only Python 3.7+.\n\n```sh\n$ pip install preacher\n$ preacher-cli --version\n```\n\nInstead of `pip`, Docker images are also available on\n[Docker Hub](https://hub.docker.com/r/ymoch/preacher)\nas `ymoch/preacher`.\nBy default, the container working directory is `/work`,\nand the host directory may be mounted here.\n\n```sh\n$ docker pull ymock/preacher\n$ docker run -v $PWD:/work ymoch/preacher preacher-cli --version\n```\n\nSecond, write your own scenario.\n\n```yaml\n# scenario.yml\nlabel: An example of a scenario\ncases:\n  - label: An example of a case\n    request: /path/to/foo\n    response:\n      status_code: 200\n      body:\n        - describe: .foo\n          should:\n            equal: bar\n```\n\nThen, run ``preacher-cli`` command.\n\n```sh\n$ preacher-cli -u http://your.domain.com/base scenario.yml\n```\n\nFor more information such as grammer of scenarios,\nsee [the full documentation][Read the Docs].\n\n## License\n\n[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)][MIT License]\n\nCopyright (c) 2019 Yu MOCHIZUKI\n\n\n[YAML]: https://yaml.org/\n[jq]: https://stedolan.github.io/jq/\n[XPath]: https://www.w3.org/TR/xpath/all/\n[Hamcrest]: http://hamcrest.org/\n[PyHamcrest]: https://pyhamcrest.readthedocs.io/\n[MIT License]: https://opensource.org/licenses/MIT\n\n[Read the Docs]: https://preacher.readthedocs.io/\n[PyPI]: https://badge.fury.io/py/preacher\n[Circle CI]: https://circleci.com/gh/ymoch/preacher\n[Codecov]: https://codecov.io/gh/ymoch/preacher\n[LGTM]: https://lgtm.com/projects/g/ymoch/preacher/context:python\n',
    'author': 'Yu Mochizuki',
    'author_email': 'ymoch.dev@gmail.com',
    'url': 'https://preacher.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
