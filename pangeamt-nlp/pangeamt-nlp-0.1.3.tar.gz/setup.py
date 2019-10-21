from setuptools import setup
import sys

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='pangeamt-nlp',
    setup_requires="setupmeta",
    author='Pangeamt'
)