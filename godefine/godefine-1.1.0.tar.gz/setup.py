#!/usr/bin/env python3

from setuptools import setup
import godefine

setup(
    name=godefine.name,
    version=godefine.version,
    author=godefine.author,
    author_email=godefine.author_email,
    url='https://github.com/ooopSnake/godefine',
    description=godefine.description,
    license='WTFPL License',
    packages=[godefine.name],
    platforms=['all'],
    python_requires='>=3.4',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    classifiers=['Framework :: Django CMS :: 3.4',
                 'Topic :: Software Development :: Code Generators',
                 'Operating System :: OS Independent'],
    install_requires=[
        'tabulate>=0.8.5',
        'wcwidth>=0.1.7'
    ],
    entry_points={
        'console_scripts': [
            'godefine = godefine.core:main '
        ]
    }

)
