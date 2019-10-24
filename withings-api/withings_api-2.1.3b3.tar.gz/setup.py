# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['withings_api']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=0.15.2', 'requests-oauth>=0.4.1', 'requests-oauthlib>=1.2']

setup_kwargs = {
    'name': 'withings-api',
    'version': '2.1.3b3',
    'description': 'Library for the Withings API',
    'long_description': "# Python withings-api [![Build status](https://github.com/vangorra/python_withings_api/workflows/Build/badge.svg?branch=master)](https://github.com/vangorra/python_withings_api/actions?workflow=Build)\nPython library for the Withings Health API\n\n\nWithings Health API\n<https://developer.withings.com/oauth2/>\n\nUses OAuth 2.0 to authenticate. You need to obtain a client id\nand consumer secret from Withings by creating an application\nhere: <http://developer.withings.com/oauth2/>\n\n## Installation\n\n    pip install withings-api\n\n## Usage\nFor a complete example, checkout the integration test in `scripts/integration_test.py`. It has a working example on how to use the API.\n```python\nfrom withings_api import WithingsAuth, WithingsApi, AuthScope\nfrom withings_api.common import get_measure_value, MeasureType\n\nauth = WithingsAuth(\n    client_id='your client id',\n    consumer_secret='your consumer secret',\n    callback_uri='your callback uri',\n    mode='demo',  # Used for testing. Remove this when getting real user data.\n    scope=(\n        AuthScope.USER_ACTIVITY,\n        AuthScope.USER_METRICS,\n        AuthScope.USER_INFO,\n        AuthScope.USER_SLEEP_EVENTS,\n    )\n)\n\nauthorize_url = auth.get_authorize_url()\n# Have the user goto authorize_url and authorize the app. They will be redirected back to your redirect_uri.\n\ncredentials = auth.get_credentials('code from the url args of redirect_uri')\n\n# Now you are ready to make calls for data.\napi = WithingsApi(credentials)\n\nmeas_result = api.measure_get_meas()\nweight_or_none = get_measure_value(meas_result, with_measure_type=MeasureType.WEIGHT)\n```\n\n## Building\nBuilding, testing and lintings of the project is all done with one script. You only need a few dependencies.\n\nDependencies:\n- python3 in your path.\n- The python3 `venv` module.\n\nThe build script will setup the venv, dependencies, test and lint and bundle the project.\n```bash\n./scripts/build.sh\n```\n\n## Integration Testing\nThere exists a simple integration test that runs against Withings' demo data. It's best to run this after you have\nsuccessful builds. \n\nNote: after changing the source, you need to run build for the integration test to pickup the changes.\n\n```bash\n./scripts/build.sh\nsource ./venv/bin/activate\n./scripts/integration_test.py --client-id <your client id> --consumer-secret <your consumer secret> --callback-uri <your clalback uri>\n```\nThe integration test will cache the credentials in a `<project root>/.credentials` file between runs. If you get an error saying\nthe access token expired, then remove that credentials file and try again.\n",
    'author': 'Robbie Van Gorkom',
    'author_email': 'robbie.van.gorkom@protonmail.com',
    'url': 'https://github.com/vangorra/python_withings_api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
