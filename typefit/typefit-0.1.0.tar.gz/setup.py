# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['typefit']

package_data = \
{'': ['*']}

extras_require = \
{'api': ['httpx>=0.7,<0.8'], 'dates': ['pendulum>=2.0,<3.0']}

setup_kwargs = {
    'name': 'typefit',
    'version': '0.1.0',
    'description': 'Fits JSON values into Python type-anotated objects',
    'long_description': '# TypeFit\n\n[![Read the Docs](https://img.shields.io/readthedocs/typefit)](http://typefit.rtfd.io/)\n[![Build Status](https://img.shields.io/travis/Xowap/typefit)](https://travis-ci.org/Xowap/typefit)\n[![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/Xowap/typefit)](https://lgtm.com/projects/g/Xowap/typefit/)\n\nTyping annotations make Python awesome, however it\'s complicated to keep your\ndata annotated when it comes from external sources like APIs. The goal of\nTypefit is to help you map that external data into type-annotated native Python\nobjects.\n\n```python\nfrom typefit import api\nfrom typing import NamedTuple, Text\n\n\nclass Item(NamedTuple):\n    id: int\n    title: Text\n\n\nclass HackerNews(api.SyncClient):\n    BASE_URL = "https://hacker-news.firebaseio.com/v0/"\n\n    @api.get("item/{item_id}.json")\n    def get_item(self, item_id: int) -> Item:\n        pass\n\nstory = HackerNews().get_item(42)\nprint(story.title)\n# An alternative to VC: &#34;Selling In&#34;\n```\n\nThis is the full example of a Hacker News API client. Its functionality is\nlimited but in 14 lines counting white space you can build a type-safe client\nfor Hacker News. You\'ll find a [full example](example/typefit_hn) attached if\nyou\'re interested.\n\n\n## Documentation\n\n[✨ **Documentation is there** ✨](http://typefit.rtfd.io/)\n\n## Licence\n\nThis library is provided under the terms of the [WTFPL](./LICENSE).\n\nIf you find it useful, you can have a look at the\n[contributors](https://github.com/Xowap/typefit/graphs/contributors) page to\nknow who helped.\n',
    'author': 'Rémy Sanchez',
    'author_email': 'remy.sanchez@hyperthese.net',
    'url': 'https://github.com/Xowap/typefit/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
