# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['spider_domainauth', 'spider_domainauth.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.0']

setup_kwargs = {
    'name': 'spkcspider-domainauth',
    'version': '0.6.2',
    'description': 'Helper for spkcspiders domain authentication',
    'long_description': '\n\nHelper for db based domain auth\n\n# Installation\n\n~~~~ sh\npip install spkcspider-domainauth\n~~~~\n\nsettings:\n\n~~~~\n...\nINSTALLED_APPS = [\n...\n    spider_domainauth\n...\n]\n\nDOMAINAUTH_URL = \'spider_domainauth:domainauth-db\'\n~~~~\n\n# Usage:\n\nurl based:\n~~~~ python\nfrom django.conf import settings\nfrom django.shortcuts import resolve_url\n\nresponse = requests.post(\n  resolve_url(settings.DOMAINAUTH_URL),\n  {\n    "urls": "http://foo/component/list/"\n  }\n)\ntoken = response.json["tokens"]["foo"]\n\n~~~~\n\n\nModule based:\n~~~~ python\nfrom spider_domainauth.models import ReverseToken\nfrom django.shortcuts import resolve_url\n\n# overloaded create method\nrtoken = ReverseToken.objects.create()\n"http://foo/token/list/?intent=domain&referrer={referrer}&payload={token}".format(\n  referrer=resolve_url(settings.DOMAINAUTH_URL),\n  token=rtoken.token\n)\ne.refresh_from_db()\n# note: it is not token but secret, reason: token is reused and prefixed with id (for uniqueness)\ne.secret\n\n~~~~\n\n\n## Settings:\n\n* DOMAINAUTH_RATELIMIT_FUNC: ratelimit access tries, can be also used to limit number of tokens\n* DOMAINAUTH_LIFETIME: token lifetime (default 1 hour) (Note: if "url based"-method is used, the token is automatically deleted afterwards)\n* DOMAINAUTH_URL: url to domain auth view (required for external users)\n\n# TODO:\n* overload other manager methods\n* better examples\n',
    'author': 'Alexander Kaftan',
    'author_email': None,
    'url': 'https://github.com/spkcspider/spkcspider-domainauth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
