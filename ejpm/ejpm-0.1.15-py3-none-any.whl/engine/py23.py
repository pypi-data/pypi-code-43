# this file contain some snippets and shortcuts to bring compatibility between python 2 and 3
# and not to jump into six or __futures

try:
    # noinspection PyUnresolvedReferences
    to_unicode = unicode
except NameError:
    to_unicode = str
