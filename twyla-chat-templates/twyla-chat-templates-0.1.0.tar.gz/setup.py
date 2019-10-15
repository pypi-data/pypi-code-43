# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['twyla', 'twyla.chat.templates']

package_data = \
{'': ['*']}

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

setup_kwargs = {
    'name': 'twyla-chat-templates',
    'version': '0.1.0',
    'description': 'A collection of Twyla chat message templates',
    'long_description': '[![image](https://img.shields.io/pypi/v/twyla-chat-templates.svg)](https://pypi.org/project/twyla-chat-templates/)\n[![image](https://img.shields.io/pypi/l/twyla-chat-templates.svg)](https://pypi.org/project/twyla-chat-templates/)\n[![image](https://img.shields.io/pypi/pyversions/twyla-chat-templates.svg)](https://pypi.org/project/twyla-chat-templates/)\n[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![](https://github.com/twyla-ai/twyla-chat-templates/workflows/Main%20Workflow/badge.svg)](https://github.com/twyla-ai/twyla-chat-templates/actions)\n\n# Twyla Chat Templates\nA collection of Twyla chat message templates\n\n## Installation\n`poetry install twyla-chat-templates`\n\n## Usage\n\n##### Quick reply buttons\n```python\nquick_replies = QuickReplies(text="Which kind of chocolate do you prefer?")\n\n# To add up to ten quick reply buttons:\nquick_replies.add(QuickReply(title="Dark", payload="dark_chocolate"))\n```\n\n##### Postback and URL Buttons\n```python\nbuttons = Buttons(text="What is your favourite type of pizza?")\n\n# To add up to three buttons:\nbuttons.add(\n        PostBackButton(title="Margherita", payload="x_Margherita_oaWVAeasEK_x"),\n        UrlButton(title="Hawaii", url="https://google.com"),\n    )\n```\n##### Generic Template\n```python\nelement = GenericElement(\n        title="Cheesecake",\n        subtitle="Cake with cheese",\n        image_url="https://cake.com/image.jpg",\n        action_url="https://cake.com",\n        buttons=[\n            PostBackButton(\n                title="I want Cheesecake", payload="x_I_want_Cheesecake_gkvMPBXXxO_x"\n            ),\n            UrlButton(title="Cheesecake, please", url="https://cheesecakeplease.com"),\n        ],\n    )\ntemplate =  GenericTemplate(elements=[element])\n```\n##### Carousel Template\n```python\n# To Create a vertically scrollable carousel, add up to 10 elements to the generic template: \ncarousel = GenericTemplate(elements=[e1, e2, e3])\n```\n\n##### Image Template \n```python\nimage = ImageTemplate(url="https://pictures.com/picture.jpg")\n```\n',
    'author': 'Twyla Engineering',
    'author_email': 'software@twyla.ai',
    'url': 'https://github.com/twyla-ai/twyla-chat-templates',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
