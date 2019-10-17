# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['opsgenie_logger']

package_data = \
{'': ['*']}

install_requires = \
['opsgenie-sdk>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'opsgenie-logger',
    'version': '0.1.4',
    'description': 'Provides a logging handler for Atlassian OpsGenie',
    'long_description': '# opsgenie-logger\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nA Python logging handler for Atlassian OpsGenie.\n\n## Basic Usage\n\n```python\nimport logging\n\nfrom opsgenie_logger import OpsGenieHandler\n\n\nlogger = logging.getLogger()\nhandler = OpsGenieHandler(api_key="integration_api_key", team_name="my_team", level=logging.ERROR)\nlogger.addHandler(handler)\nlogger.error("This will go to OpsGenie!")\ntry:\n    raise ValueError("This is a problem")\nexcept ValueError:\n    logger.exception("This stack trace is going to OpsGenie")\n```\n\n## Contribution Guidelines\n - Any changes should be covered with a unit test and documented in [CHANGELOG.md]\n\n## Release Process\n1. Start a release with Git Flow\n1. Update the version number using Semantic Versioning in `pyproject.toml` and `__init__.py`\n1. Ensure all dependencies are pointing to released versions\n1. Update the release notes in [CHANGELOG.md]\n    1. Move changes from "Unreleased" to a section with appropriate version #\n    1. Add a link at the bottom of the page to view this version in GitHub.\n1. Commit and push any changes\n1. Create a pull request from the release branch to master\n1. Ensure all checks pass (e.g. CircleCI)\n1. Open and merge the pull request\n1. Create a tag on the merge commit with the release number\n\n## Contributors \n - Dylan Anthony <danthony@triaxtec.com>\n\n\n[CHANGELOG.md]: docs/CHANGELOG.md\n',
    'author': 'Dylan Anthony',
    'author_email': 'danthony@triaxtec.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
