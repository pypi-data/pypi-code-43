import importlib
from photo_dl import re


parsers = ['meituri']


def url2parser(url):
    for parser in parsers:
        if re.match(parser, url):
            return importlib.import_module('.' + parser, __package__)
    return None
