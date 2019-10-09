# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ms_graph_exporter', 'ms_graph_exporter.celery', 'ms_graph_exporter.ms_graph']

package_data = \
{'': ['*']}

install_requires = \
['adal>=1.2,<2.0',
 'celery-redbeat>=0.13,<0.14',
 'celery>=4.3,<5.0',
 'gevent>=1.4,<2.0',
 'pyyaml>=3.13,<4.0',
 'redis>=3.3,<4.0',
 'requests>=2.20,<3.0',
 'typing>=3.7,<4.0']

extras_require = \
{'docs': ['recommonmark>=0.5.0,<0.6.0',
          'sphinx>=2.2,<3.0',
          'sphinx-autodoc-typehints>=1.8,<2.0'],
 'test': ['pytest>=5.1,<6.0',
          'pytest-benchmark[aspect]>=3.2,<4.0',
          'pytest-cov>=2.7,<3.0',
          'pytest-dockerc>=1.0,<2.0',
          'pytest-instafail>=0.4,<0.5',
          'pytest-lazy-fixture>=0.5,<0.6',
          'pytest-random-order>=1.0,<2.0']}

setup_kwargs = {
    'name': 'ms-graph-exporter',
    'version': '0.1.0rc4.dev201910092',
    'description': 'A distributed Celery application to export time-domain data periodically from Microsoft Graph API into a buffer key-value store.',
    'long_description': '# MsGraphExporter\n\n[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)][PythonRef] [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)][BlackRef] [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)][MITRef]\n[![ReadTheDocs](https://readthedocs.org/projects/msgraphexporter/badge/?version=latest)][DocsRef] [![Build Status](https://dev.azure.com/undp/MsGraphExporter/_apis/build/status/MsGraphExporter_Github?branchName=develop)][BuildStatusRef]\n\n[PythonRef]: https://docs.python.org/3.6/\n[BlackRef]: https://github.com/ambv/black\n[MITRef]: https://opensource.org/licenses/MIT\n[DocsRef]: https://msgraphexporter.readthedocs.io/en/latest/\n[BuildStatusRef]: https://dev.azure.com/undp/MsGraphExporter/_build/latest?definitionId=21&branchName=develop\n\n`MsGraphExporter` is an application that performs periodic export of time-domain data like Azure AD user signins from [Microsoft Graph API][MsGraphApiDoc] into a buffer key-value store (currently supports [Redis][RedisRef]) for subsequent processing. It uses [Celery][CeleryProjectRef] task queue for parallel processing, [gevent][GeventRef] greenlets for concurrent uploads, relies on the [Graph API pagination][MsGraphApiPage] to control memory footprint and respects [Graph API throttling][MsGraphApiThrottle]. The application could be deployed as a single-container worker or as a set of multiple queue-specific workers for high reliability and throughput.\n\n[MsGraphApiDoc]: https://docs.microsoft.com/en-us/graph/overview\n[MsGraphApiPage]: https://docs.microsoft.com/en-us/graph/paging\n[MsGraphApiThrottle]: https://docs.microsoft.com/en-us/graph/throttling\n\n## Getting Started\n\nFollow these instructions to use the application.\n\n### Installing\n\n`MsGraphExporter` is distributed through the [Python Package Index][PyPIRef] as [ms-graph-exporter][PyPIProjRef]. Run the following command to:\n\n[PyPIRef]: https://pypi.org\n[PyPIProjRef]:https://pypi.org/project/ms-graph-exporter/\n\n* install a specific version\n\n    ```sh\n    pip install "ms-graph-exporter==0.1"\n    ```\n\n* install the latest version\n\n    ```sh\n    pip install "ms-graph-exporter"\n    ```\n\n* upgrade to the latest version\n\n    ```sh\n    pip install --upgrade "ms-graph-exporter"\n    ```\n\n* install optional DEV dependencies like `pytest` framework and plugins necessary for performance and functional testing\n\n    ```sh\n    pip install "ms-graph-exporter[test]"\n    ```\n\n`MsGraphExporter` is also distributed as the Alpine-based docker container and published on [Docker Hub][DockerHubRef] as [undp/ms-graph-exporter][DockerHubProjRef].\n\n[DockerHubRef]: https://hub.docker.com/\n[DockerHubProjRef]: https://hub.docker.com/r/undp/ms-graph-exporter\n\n`Service Principal` credentials with correct access rights to `Graph API` must be defined for `docker/docker-compose.yaml`example deployment to work. Following `.env` file should be placed at the root of the project folder, or following ENV variables defined in other way:\n\n```sh\nGRAPH_CLIENT_ID=<clientId>\nGRAPH_CLIENT_SECRET=<clientSecret>\nGRAPH_TENANT=<tenant>\n```\n\nThen, docker deployment could be initiated with:\n\n```sh\ndocker-compose --file docker/docker-compose.yaml up\n```\n\n### Requirements\n\n* Python >= 3.6\n\n## Built using\n\n* [Celery][CeleryProjectRef] - Distributed task queue\n* [gevent][GeventRef] - concurrent data upload to [Redis][RedisRef]\n* [redis-py][RedisPyGithub] - Python interface to [Redis][RedisRef]\n\n[RedisRef]: https://redis.io/\n[CeleryProjectRef]:http://www.celeryproject.org/\n[GeventRef]: http://www.gevent.org\n[RedisPyGithub]: https://github.com/andymccurdy/redis-py\n\n## Versioning\n\nWe use [Semantic Versioning Specification][SemVer] as a version numbering convention.\n\n[SemVer]: http://semver.org/\n\n## Release History\n\nFor the available versions, see the [tags on this repository][RepoTags]. Specific changes for each version are documented in [CHANGELOG.md][ChangelogRef].\n\nAlso, conventions for `git commit` messages are documented in [CONTRIBUTING.md][ContribRef].\n\n[RepoTags]: https://github.com/undp/MsGraphExporter/tags\n[ChangelogRef]: CHANGELOG.md\n[ContribRef]: CONTRIBUTING.md\n\n## Authors\n\n* **Oleksiy Kuzmenko** - [OK-UNDP@GitHub][OK-UNDP@GitHub] - *Initial design and implementation*\n\n[OK-UNDP@GitHub]: https://github.com/OK-UNDP\n\n## Acknowledgments\n\n* Hat tip to all individuals shaping design of this project by sharing their knowledge in articles, blogs and forums.\n\n## License\n\nUnless otherwise stated, all authors (see commit logs) release their work under the [MIT License][MITRef]. See [LICENSE.md][LicenseRef] for details.\n\n[LicenseRef]: LICENSE.md\n\n## Contributing\n\nThere are plenty of ways you could contribute to this project. Feel free to:\n\n* submit bug reports and feature requests\n* outline, fix and expand documentation\n* peer-review bug reports and pull requests\n* implement new features or fix bugs\n\nSee [CONTRIBUTING.md][ContribRef] for details on code formatting, linting and testing frameworks used by this project.\n',
    'author': 'Oleksiy Kuzmenko',
    'author_email': 'oleksiy.kuzmenko@undp.org',
    'url': 'https://github.com/undp/MsGraphExporter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
