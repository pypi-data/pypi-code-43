import os
from setuptools import setup


setup(
    name='decklist',
    version='0.1.0',
    author='Dylan Stephano-Shachter',
    author_email='dylan@theone.ninja',
    description='A library for parsing decklists',
    license='GPL',
    url='https://github.com/dstathis/decklist',
    packages=['decklist'],
    long_description=open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
    ).read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta'
    ]
)
