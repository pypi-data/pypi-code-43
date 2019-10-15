#!/usr/bin/env python3

from setuptools import setup

setup(
    name='godefine',
    version='1.0.5',
    author='suzhen',
    author_email='suzhen@gmail.com',
    url='https://github.com/ooopSnake/godefine',
    description=u'preprocess marcos tool',
    license='WTFPL License',
    packages=['godefine'],
    platforms=['all'],
    python_requires='>=3.0',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    classifiers=['Programming Language :: Python :: 3',
                 'Topic :: Software Development :: Code Generators',
                 'Operating System :: OS Independent'],
    install_requires=[
        'tabulate>=0.8.5',
        'wcwidth>=0.1.7'
    ],
    entry_points={
        'console_scripts': [
            'godefine = godefine.godefine:main '
        ]
    }

)
