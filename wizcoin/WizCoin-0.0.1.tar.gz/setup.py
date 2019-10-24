from setuptools import setup
import os
import re

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as fileObj:
    long_description = fileObj.read()

# Load version from module (without loading the whole module)
with open('src/wizcoin/__init__.py', 'r') as fileObj:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fileObj.read(), re.MULTILINE).group(1)

setup(
    name='WizCoin',
    version=version,
    description=('WizCoin is a module for handling wizard currency.'),
    long_description=long_description,
    url='https://github.com/asweigart/wizcoin',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    packages=['src/wizcoin'],
    license='BSD',
    keywords="wizard currency galleon sickle knut",
    test_suite='tests',
    install_requires=[],
)