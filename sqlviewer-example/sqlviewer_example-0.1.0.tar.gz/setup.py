import os
from setuptools import setup

requires = [
    "sqlviewer"
]

setup(
    name='sqlviewer_example',
    install_requires=requires,
    version="0.1.0",
    description="Example connector to sqlviewer to demonstrate extendibility",

    author="Kieran Bacon",
    author_email="kieran.bacon@outlook.com",

    packages=['sqlviewer_example'],

    entry_points={
        'sqlviewer_connectors': [
            'example = sqlviewer_example.example:ExampleConnector'
        ]
    }
)