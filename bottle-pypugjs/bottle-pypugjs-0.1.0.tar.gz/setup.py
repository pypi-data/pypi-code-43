# coding: utf-8
import re
from os import path as op

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

def _find(value, text):
    try:
        return re.search(r'^%s\s*=\s*"(.*)"' %value, text, re.M).group(1)
    except AttributeError:
        try:
            return re.search(r"^%s\s*=\s*'(.*)'" %value, text, re.M).group(1)
        except AttributeError:
            return ''

_meta = _read('bottle_pypugjs.py')
py_modules=['bottle_pypugjs']

setup(
    name=_find('__project__', _meta),
    version=_find('__version__', _meta),
    author=_find('__autor__', _meta),
    author_email=_find('__email__', _meta),
    description=_read('DESCRIPTION') or _find('__description__', _meta),
    long_description=_read('README.rst'),
    long_description_content_type="text/markdown",
    license=_read('LICENSE') or _find('__license__', _meta),
    py_modules=py_modules,
    install_requires=[l for l in _read('requirements.txt').split('\n') if l and not l.startswith('#')]
)
