# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blogger_cli',
 'blogger_cli.blog_manager',
 'blogger_cli.cli_utils',
 'blogger_cli.commands',
 'blogger_cli.commands.convert_utils',
 'blogger_cli.commands.export_utils',
 'blogger_cli.converter',
 'blogger_cli.resources',
 'blogger_cli.tests']

package_data = \
{'': ['*'],
 'blogger_cli.commands': ['feed_utils/*'],
 'blogger_cli.resources': ['blog_layout/*',
                           'blog_layout/_blogger_templates/*',
                           'blog_layout/assets/css/*',
                           'blog_layout/blog/*'],
 'blogger_cli.tests': ['tests_resources/*',
                       'tests_resources/_blogger_templates/*',
                       'tests_resources/index/*',
                       'tests_resources/results/*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'click>=7.0,<8.0',
 'feedgen>=0.8.0,<0.9.0',
 'markdown>=3.1,<4.0',
 'misspellings>=1.5,<2.0',
 'nbconvert>=5.5,<6.0',
 'pyspellchecker>=0.5.0,<0.6.0',
 'selectolax>=0.2.1,<0.3.0']

entry_points = \
{'console_scripts': ['blogger = blogger_cli.cli:cli']}

setup_kwargs = {
    'name': 'blogger-cli',
    'version': '1.2.0',
    'description': 'Blogger cli is a CLI tool to convert ipynb, md, html file to responsive html files.',
    'long_description': "# Blogger-cli\nA custom cli tool to process jupyter notebooks, markdown files and html files. Write your blog in markdown or jupyter notebooks and then transform into blog post with mathjax, code support, google analytics, navigation, disqus support.\n\nSee a sample blog made by blogger-cli: [Here](https://pykancha.github.io/test/)\n\n## Why?\nIt is easy to get your hands on, works flawlessly and won't get bulky and slow overtime.\nBlogger-cli has a simple conversion system that is fast as well as extremely customizable.\n\n\n## Features\n* Robust conversion of ipynb notebooks with great support for mobile devices as well.\n* Built-in support for disqus, google analytics, navigation bar, social sharing, mathjax and code highlighting.\n* Support for spell checking, live server and generation of rss/atom feeds.\n* Blog management: updating index, parsing out images, managing topics and metadata.\n* Write and post blogs from android or any micro device. All that is required is command line with python and pip.\n* Built in design, blog_templates for rapidly setting up your blog from scratch.\n* Fully customizable with support for custom themes and templates.\n* Also support conversion of other file formats like markdown. You can also implement your own.\n\n\n## 💻 Installation\n\n### Recommended Method\n```\n$ curl -sSL https://hemanta212.github.io/blogger-cli/get_blogger.py | python\n```\nSince blogger has alot of dependecies (nbconvert, jupyter), this custom installer will install them in a virtual environment and add it to your path for global access.\n\n### Using pip\n```\npip install blogger-cli\n```\n\nIf you mainly use jupyter notebooks, then you already have all the required dependencies although it is recommended to use `virutal environments`.\n\n\n## 🚀 Getting Started\nMake a website repository and clone it to your computer. Now register your blog name with blogger\n```$ blogger addblog <blogname>```\nand setup necessary configs. Now, If you have new site or empty site. You can get blogger default design and boilerplate.\n```\n$ blogger export blog_layout -b <blogname>\n```\nNow, all assets will be moved to the blog_dir you specified in the blog config during setup.\n```\n$ blogger serve <blogname>\n```\nOpen the url http://localhost:8000/ in your browser to view your blog!!\n\n## 📖 Documentation\n- [Installation, update, uninstall methods](docs/installation.md)\n- [Managing blogs and configurations](docs/blog_management.md)\n- [Conversion of files and folders](docs/conversion.md)\n- [Serving blog locally](docs/serving_blog_locally.md)\n- [Using export command](docs/export.md)\n- [Customizing templates and design](docs/customizing.md)\n- [Writing blog's metadata](docs/meta.md)\n- [Using spellcheck](docs/spellcheck.md)\n- [Generating feed for your blog](docs/feed.md)\n- [Advanced optional configurations](docs/optional_config.md)\n- [Recommended workflow for blogger-cli](docs/workflow.md)\n\n> View docs in: [website](https://hemanta212.github.io/blogger-cli/)\n\n## Author\n\n👤 **Hemanta Sharma**\n- Github: [@hemanta212](https://github.com/hemanta212)\n\n## Special Thanks\n\n👤 **Nipun Batra** : Inspiration for core conversion mechanism and design resources.\n- Github: [@nipunbatra](https://github.com/nipunbatra)\n- His article on ipynb conversion: [@nipunbatra.github.io](https://nipunbatra.github.io/blog/2017/Jupyter-powered-blog.html)\n\n## Show your support\n\nPlease ⭐️ this repository if this project helped you!\n\n## 📝 License\nCopyright © 2019 [Hemanta Sharma](https://github.com/hemanta212).<br />\nThis project is [MIT](LICENSE) licensed.\n---\n",
    'author': 'hemanta212',
    'author_email': 'sharmahemanta.212@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hemanta212/blogger-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
