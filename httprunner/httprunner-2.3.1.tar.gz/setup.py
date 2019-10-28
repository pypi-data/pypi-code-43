# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['httprunner', 'httprunner.plugins', 'httprunner.plugins.locusts']

package_data = \
{'': ['*'], 'httprunner': ['static/*']}

install_requires = \
['colorama>=0.4.1,<0.5.0',
 'colorlog>=4.0.2,<5.0.0',
 'filetype>=1.0.5,<2.0.0',
 'har2case>=0.3.1,<0.4.0',
 'jinja2>=2.10.3,<3.0.0',
 'jsonpath>=0.82,<0.83',
 'pyyaml>=5.1.2,<6.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.22.0,<3.0.0']

extras_require = \
{':python_version >= "2.7" and python_version < "2.8"': ['future>=0.18.1,<0.19.0']}

entry_points = \
{'console_scripts': ['ate = httprunner.cli:main',
                     'hrun = httprunner.cli:main',
                     'httprunner = httprunner.cli:main',
                     'locusts = httprunner.plugins.locusts.cli:main']}

setup_kwargs = {
    'name': 'httprunner',
    'version': '2.3.1',
    'description': 'One-stop solution for HTTP(S) testing.',
    'long_description': "\n# HttpRunner\n\n[![downloads](https://pepy.tech/badge/httprunner)](https://pepy.tech/project/httprunner)\n[![travis-ci](https://travis-ci.org/httprunner/httprunner.svg?branch=master)](https://travis-ci.org/httprunner/httprunner)\n[![coveralls](https://coveralls.io/repos/github/HttpRunner/HttpRunner/badge.svg?branch=master)](https://coveralls.io/github/HttpRunner/HttpRunner?branch=master)\n[![pypi version](https://img.shields.io/pypi/v/httprunner.svg)](https://pypi.python.org/pypi/httprunner)\n[![pyversions](https://img.shields.io/pypi/pyversions/httprunner.svg)](https://pypi.python.org/pypi/httprunner)\n[![TesterHome](https://img.shields.io/badge/TTF-TesterHome-2955C5.svg)](https://testerhome.com/github_statistics)\n\n*HttpRunner* is a simple & elegant, yet powerful HTTP(S) testing framework. Enjoy! ✨ 🚀 ✨\n\n## Design Philosophy\n\n- Embrace open source, stand on giants' shoulders, like [`Requests`][Requests], [`unittest`][unittest] and [`Locust`][Locust].\n- Convention over configuration.\n- Pursuit of high rewards, write once and achieve a variety of testing needs\n\n## Key Features\n\n- Inherit all powerful features of [`Requests`][Requests], just have fun to handle HTTP(S) in human way.\n- Define testcases in YAML or JSON format in concise and elegant manner.\n- Record and generate testcases with [`HAR`][HAR] support. see [`har2case`][har2case].\n- Supports `variables`/`extract`/`validate` mechanisms to create full test scenarios.\n- Supports perfect hook mechanism.\n- With `debugtalk.py` plugin, very easy to implement complex logic in testcase.\n- Testcases can be run in diverse ways, with single testcase, multiple testcases, or entire project folder.\n- Test report is concise and clear, with detailed log records.\n- With reuse of [`Locust`][Locust], you can run performance test without extra work.\n- CLI command supported, perfect combination with `CI/CD`.\n\n## Documentation\n\nHttpRunner is rich documented.\n\n- [`中文用户使用手册`][user-docs-zh]\n- [`开发历程记录博客`][development-blogs]\n\n## How to Contribute\n\n1. Check for [open issues](https://github.com/httprunner/httprunner/issues) or [open a fresh issue](https://github.com/httprunner/httprunner/issues/new/choose) to start a discussion around a feature idea or a bug.\n2. Fork [the repository](https://github.com/httprunner/httprunner) on GitHub to start making your changes to the **master** branch (or branch off of it). You also need to comply with the [development rules](https://github.com/httprunner/docs/blob/master/en/docs/dev-rules.md).\n3. Write a test which shows that the bug was fixed or that the feature works as expected.\n4. Send a pull request, you will then become a [contributor](https://github.com/httprunner/httprunner/graphs/contributors) after it gets merged and published.\n\n## Subscribe\n\n关注 HttpRunner 的微信公众号，第一时间获得最新资讯。\n\n![](httprunner/static/qrcode.jpg)\n\n[Requests]: http://docs.python-requests.org/en/master/\n[unittest]: https://docs.python.org/3/library/unittest.html\n[Locust]: http://locust.io/\n[har2case]: https://github.com/httprunner/har2case\n[user-docs-zh]: http://cn.httprunner.org/\n[development-blogs]: http://debugtalk.com/tags/httprunner/\n[HAR]: http://httparchive.org/\n[Swagger]: https://swagger.io/\n\n",
    'author': 'debugtalk',
    'author_email': 'debugtalk@gmail.com',
    'url': 'https://github.com/HttpRunner/HttpRunner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
