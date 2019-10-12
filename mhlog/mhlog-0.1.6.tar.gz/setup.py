import mhlog
from setuptools import setup

long_description = '''mhlog is a simple logging library, see https://gitlab.com/mhmorgan/pymhlog'''

setup(
    name='mhlog',
    version=mhlog.__version__,
    copyright=mhlog.__copyright__,
    author=mhlog.__author__,
    author_email=mhlog.__author_email__,
    description=mhlog.__description__,
    long_description=long_description,
    packages=['mhlog'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)
