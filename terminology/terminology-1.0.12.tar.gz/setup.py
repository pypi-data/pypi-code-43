# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['terminology']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'terminology',
    'version': '1.0.12',
    'description': 'An intuitive way to color terminal text',
    'long_description': '# Terminology\n\n[![Build Status](https://travis-ci.org/juanrgon/terminology.svg?branch=master)](https://travis-ci.org/juanrgon/terminology)\n\nA simple way to color terminal text! ❤️ 💛 💚 💙 💜\n\n## Color Text\n\n```python\nfrom terminology import in_red, in_yellow, in_green, in_blue, in_magenta\n\nprint(in_red("it\'s"), in_yellow("a"), in_green("double"), in_blue("rainbow"), in_magenta("dude..."))\n```\n\n_Output_\n\n![alt text][coloring]\n\n[coloring]: https://raw.githubusercontent.com/juanrgon/terminology/master/pics/coloring.png\n "Coloring"\n\n## Color Text Background\n\n```python\nfrom terminology import on_green, on_yellow, on_red\n\nprint(on_green("OK"), on_yellow("WARNING"), on_red("DANGER")\n```\n\n_Output_\n\n![alt text][background colors]\n\n[background colors]: https://raw.githubusercontent.com/juanrgon/terminology/master/pics/background.png\n "Background Colors"\n\n## Emphasize Text with Bold and Underlining\n\n```python\nfrom terminology import bold, underlined\n\nprint(in_bold("Chapter 1"))\nprint("- ", underlined("Section i"))\nprint("- ", underlined("Section ii"), "\\n")\n\nprint(in_bold("Chapter 2"))\nprint("- ", underlined("Section i"), \'\\n\')\n```\n\n_Output_\n\n![alt text][bold and underline]\n\n[bold and underline]: https://raw.githubusercontent.com/juanrgon/terminology/master/pics/bold_and_underline.png\n "Bold and Underline"\n',
    'author': 'Juan Gonzalez',
    'author_email': 'jrg2156@gmail.com',
    'url': 'https://github.com/juanrgon/terminology',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
