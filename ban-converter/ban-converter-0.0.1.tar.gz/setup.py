import io
from setuptools import find_packages, setup

from ban_converter import __version__

with io.open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ban-converter',
    version=__version__,
    author='Carl Mattsson',
    author_email='carl.mattsson@gmail.com',
    description='A simple BBAN <-> IBAN converter for bank account numbers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/carlmatt/ban-converter',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English'
    ],
    python_requires='>=3',
)
