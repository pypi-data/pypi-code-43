# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cognite', 'cognite.replicator']

package_data = \
{'': ['*']}

install_requires = \
['cognite-sdk>=1.1.6,<2.0.0', 'google-cloud-logging>=1.12,<2.0']

entry_points = \
{'console_scripts': ['replicator = cognite.replicator.__main__:main']}

setup_kwargs = {
    'name': 'cognite-replicator',
    'version': '0.5.0',
    'description': 'Python package for replicating data across CDF tenants. Copyright 2019 Cognite AS',
    'long_description': '<a href="https://cognite.com/">\n    <img src="https://raw.githubusercontent.com/cognitedata/cognite-python-docs/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />\n</a>\n\n# Cognite Python Replicator\n[![build](https://webhooks.dev.cognite.ai/build/buildStatus/icon?job=github-builds/cognite-replicator/master)](https://jenkins.cognite.ai/job/github-builds/job/cognite-replicator/job/master/)\n[![codecov](https://codecov.io/gh/cognitedata/cognite-replicator/branch/master/graph/badge.svg)](https://codecov.io/gh/cognitedata/cognite-replicator)\n[![Documentation Status](https://readthedocs.com/projects/cognite-cognite-replicator/badge/?version=latest)](https://cognite-cognite-replicator.readthedocs-hosted.com/en/latest/)\n[![PyPI version](https://badge.fury.io/py/cognite-replicator.svg)](https://pypi.org/project/cognite-replicator/)\n[![tox](https://img.shields.io/badge/tox-3.6%2B-blue.svg)](https://www.python.org/downloads/release/python-366/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cognite-replicator)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nCognite Replicator is a Python package for replicating data across Cognite Data Fusion (CDF) projects. This package is\nbuilt on top of the Cognite Python SDK.\n\nCopyright 2019 Cognite AS\n\n## Prerequisites\nIn order to start using the Replicator, you need:\n* Python3 (>= 3.6)\n* Two API keys, one for your source tenant and one for your destination tenant. Never include the API key directly in the code or upload the key to github. Instead, set the API key as an environment variable.\n\nThis is how you set the API key as an environment variable on Mac OS and Linux:\n```bash\n$ export COGNITE_SOURCE_API_KEY=<your source API key>\n$ export COGNITE_DESTINATION_API_KEY=<your destination API key>\n```\n\n## Installation\nThe replicator is available on PyPI, and can also be executed as a standalone script.\n\nTo install it as a Python library that can be run from command line:\n```bash\npip install cognite-replicator\npython -m cognite.replicator\n```\n\nBuild and run it as a docker container:\n```bash\ndocker build -t cognite-replicator .\ndocker run -it cognite-replicator\n```\n\nFor *Databricks* you can install it on a cluster. First, click on **Libraries** and **Install New**.  Choose your library type to be **PyPI**, and enter **cognite-replicator** as Package. Let the new library install and you are ready to replicate!\n\n\n## Usage\n\n### Setup as Python library\n```python\nimport os\n\nfrom cognite.client import CogniteClient\nfrom cognite.replicator import assets, events, time_series, datapoints\n\nSRC_API_KEY = os.environ.get("COGNITE_SOURCE_API_KEY")\nDST_API_KEY = os.environ.get("COGNITE_DESTINATION_API_KEY")\nPROJECT_SRC = "Name of source tenant"\nPROJECT_DST = "Name of destination tenant"\nCLIENT_NAME = "cognite-replicator"\nBATCH_SIZE = 10000 # this is the max size of a batch to be posted\nNUM_THREADS= 10 # this is the max number of threads to be used\n\nCLIENT_SRC = CogniteClient(api_key=SRC_API_KEY, project=PROJECT_SRC, client_name=CLIENT_NAME)\nCLIENT_DST = CogniteClient(api_key=DST_API_KEY, project=PROJECT_DST, client_name=CLIENT_NAME, timeout=90)\n\nassets.replicate(CLIENT_SRC, CLIENT_DST)\nevents.replicate(CLIENT_SRC, CLIENT_DST, BATCH_SIZE, NUM_THREADS)\ntime_series.replicate(CLIENT_SRC, CLIENT_DST, BATCH_SIZE, NUM_THREADS)\ndatapoints.replicate(CLIENT_SRC, CLIENT_DST)\n```\n\n### Run it from databricks notebook\n```python\nimport logging\n\nfrom cognite.client import CogniteClient\nfrom cognite.replicator import assets, configure_databricks_logger\n\nSRC_API_KEY = dbutils.secrets.get("cdf-api-keys", "source-tenant")\nDST_API_KEY = dbutils.secrets.get("cdf-api-keys", "destination-tenant")\n\nCLIENT_SRC = CogniteClient(api_key=SRC_API_KEY, client_name="cognite-replicator")\nCLIENT_DST = CogniteClient(api_key=DST_API_KEY, client_name="cognite-replicator")\n\nconfigure_databricks_logger(log_level=logging.INFO)\nassets.replicate(CLIENT_SRC, CLIENT_DST)\n```\n\n## Changelog\nWondering about upcoming or previous changes? Take a look at the [CHANGELOG](https://github.com/cognitedata/cognite-replicator/blob/master/CHANGELOG.md).\n\n## Contributing\nWant to contribute? Check out [CONTRIBUTING](https://github.com/cognitedata/cognite-replicator/blob/master/CONTRIBUTING.md).\n',
    'author': 'Even Wiik Thomassen',
    'author_email': 'even.thomassen@cognite.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
