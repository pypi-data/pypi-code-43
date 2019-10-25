# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['breakword']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'breakword',
    'version': '0.2.0',
    'description': 'Mixing breakpoints with print debugging.',
    'long_description': '\n# breakword\n\n\n## A description of the problem\n\nLet\'s say you have a bug somewhere in your code, but it doesn\'t raise an exception and you\'re not entirely sure where things went wrong, so you start peppering your code with print statements in order to get an idea of what\'s going on.\n\nAt some point you see something wrong. You would like to investigate closer.\n\nHowever, it seems to happen on the 174th iteration of some loop, and you\'re not entirely sure how to make a breakpoint that triggers right where something went wrong, and not before. It\'s not clear what condition to write for the breakpoint. You don\'t know what to do except print more stuff.\n\nNow, what if you had two commands:\n\n* `breakword.log()`, a function to print some easily identifiable word.\n* `breakword.brk(word)`, a function to break after some word has been printed.\n\nThen you\'d just run the script once, see that something happens after the word `potato`, and then you\'d set a breakpoint to trigger after that word, and run the script again (hopefully your script is deterministic -- if it isn\'t, only God can help you).\n\nThat\'s basically what this library does.\n\n\n## Least-effort API\n\nThe `PYTHONBREAKPOINT` environment variable tells Python what to call when it sees `breakpoint()`. You can set it to `breakword.logbrk` to get some magic.\n\nThe `BREAKWORD` environment variable tells `breakword` which word to break on. If not set, no breakpoints will be entered unless explicitly specified in the Python code.\n\nBasically, do this:\n\n```bash\n# Install the library\npip install breakword\n# Run the script without entering a breakpoint\nenv PYTHONBREAKPOINT=breakword.logbrk python yourscript.py\n# Run the script and break on the word "fish"\nenv PYTHONBREAKPOINT=breakword.logbrk BREAKWORD=fish python yourscript.py\n```\n\nHere\'s a screenshot to show what it looks like:\n\n![demo](https://raw.githubusercontent.com/breuleux/breakword/master/media/demo.png)\n\n\n## Marginally-more-effort API\n\n\n* `breakword.log(*things, **config)`: Print a word and optionally other things after it.\n\n* `breakword.brk(word=None, **config)`: Sets a breakpoint to trigger after `log` printed out the given word. If `word` is `None` or not given, the `BREAKWORD` environment variable is consulted. If the variable is not set, nothing will happen.\n  * This is equivalent to `breakword.after(word).breakpoint()`.\n\n* `breakword.after(word=None, **config)`: Returns an object that evaluates to `True` right after `log` printed out the given word. As with `brk`, if `word` is `None` or not given, the `BREAKWORD` environment variable is consulted.\n\n* `breakword.word(**config)`: Returns the next word as a string. You can print it yourself, in which case it\'s basically like `log`, or you can store it in an object.\n\n* `breakword.logbrk(**config)`: Calls `log` and then `brk`.\n\n* `breakword.wordbrk(**config)`: Calls `word` and then `brk`. The word is returned.\n\n* `breakword.set_default_logger(logger)`: Set the logging function to use (defaults to `print`)\n\n![demo](https://raw.githubusercontent.com/breuleux/breakword/master/media/demo2.png)\n\n\n### Configuration\n\n`log`, `word`, `after` and `brk` all take keyword arguments:\n\n* `group`: A string that represents a "group" for the words. Each group is independent: `log(group="abc")` and `log(group="xyz")` will not interfere with each other, so you can add more `log` statements in your code without changing the words printed out by the existing logs.\n  * You can also do something like: `if after("fish"): log(group="xyz")`. That statement will log extra words, but only after "fish" in the main sequence.\n  * Different groups will (probably) have different colors, to help telling them apart.\n\n* `logger` The logger to use. Defaults to the default logger, which is `print`.\n',
    'author': 'Olivier Breuleux',
    'author_email': 'breuleux@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
