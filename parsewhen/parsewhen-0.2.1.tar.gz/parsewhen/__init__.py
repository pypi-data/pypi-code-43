'''Python package `parsewhen` parses arbitrary text and attempts to convert sections
to datetime or timedelta objects. If nothing can be parsed the original text is returned.

.. include:: ../docs/usage.md
'''

from . import lexer, parser, errors, walker
from . import eval as evil

from .language import Language
from .parsewhen import generate, replace, parse, range, tree
