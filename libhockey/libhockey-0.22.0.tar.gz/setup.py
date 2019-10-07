# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['libhockey']

package_data = \
{'': ['*']}

install_requires = \
['deserialize>=0.10.0,<0.11.0', 'requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'libhockey',
    'version': '0.22.0',
    'description': 'A Python wrapper around the Hockey App API.',
    'long_description': '# This project has been deprecated\nDue to the immenent switch from Hockey to App Center, this project has been deprecated. Minor updates may still be made, but these should not be counted on in any way. No pull requests will be accepted at this point. Any issues are unlikely to be addressed.\n\n\n# libhockey\n\n[![PyPi Version](https://img.shields.io/pypi/v/libhockey.svg)](https://pypi.org/project/libhockey/)\n[![License](https://img.shields.io/pypi/l/libhockey.svg)](https://github.com/Microsoft/libhockey/blob/master/LICENSE)\n\n\n\n`libhockey` is a wrapper around the Hockey App REST API. It\'s aim is to be a simple and easy to use as possible.\n\nIt doesn\'t cover every single API, but does the basics. Feel free to open an issue or a pull request for API support.\n\n## Getting started\n\nJust add the following and you are ready to go:\n\n```python\n\nimport libhockey\n\nclient = libhockey.HockeyClient(access_token="...")\n```\n\n## Examples\n\n#### Listing all versions of an app\n\n```python\nfor version in client.versions.generate_all("[app id]"):\n    print(version.download_url)\n```\n\n#### Uploading a build\n\n```python\ndownload_link = client.versions.upload("/path/to/app.ipa", "Release notes go here")\n```\n\n#### Find new crashes in a build\n\n```python\n\ncurrent_crashes = client.crashes.groups_for_version("[app id]", "[current version id]")\nprevious_crashes = client.crashes.groups_for_version("[app id]", "[previous version id]")\nnew_crashes = list(set(current_crashes) - set(previous_crashes))\n\nfor crash in new_crashes:\n    print(f"({crash.number_of_crashes}) {crash.crash_file} - {crash.crash_class}:{crash.crash_method}")\n```\n\n\n# Contributing\n\nThis project welcomes contributions and suggestions.  Most contributions require you to agree to a\nContributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us\nthe rights to use your contribution. For details, visit https://cla.microsoft.com.\n\nWhen you submit a pull request, a CLA-bot will automatically determine whether you need to provide\na CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions\nprovided by the bot. You will only need to do this once across all repos using our CLA.\n\nThis project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).\nFor more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or\ncontact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.\n',
    'author': 'Dale Myers',
    'author_email': 'dalemy@microsoft.com',
    'url': 'https://github.com/Microsoft/libhockey',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
