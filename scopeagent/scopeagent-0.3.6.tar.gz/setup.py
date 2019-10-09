import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'VERSION'), "r") as fh:
    version = fh.read()

with open(os.path.join(os.path.dirname(__file__), 'README.md'), "r") as fh:
    long_description = fh.read()

test_requirements = [
    'mock',
    'pytest',
    'pytest-localserver',
    # 'pytest-mock',

    # Instrumented libraries to be tested
    'requests',
    'psycopg2-binary',
    'sqlalchemy',
]

setup(
    name='scopeagent',
    version=version,
    url='https://scope.dev',
    license='Apache',
    author='Undefined Labs, Inc',
    author_email='info@undefinedlabs.com',
    description='Scope agent for Python',
    install_requires=[
        'certifi>=2018.8.24',
        'msgpack>=0.6.1,<1.0',
        'opentracing>=2.0.0,<3.0',
        'six>=1.10.0,<2.0',
        'urllib3>=1.23',
        'wrapt>=1.10.11',
    ],
    packages=find_packages(exclude=('tests',)),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
    ),
    entry_points={
        'console_scripts': [
            'scope-run = scopeagent.cli.__main__:main',
        ],
    },
    extras_require={
        'tests': test_requirements,
        'docs': [
            'Sphinx',
            'sphinx-argparse',
            'sphinx-rtd-theme',
        ]
    },
    setup_requires=['wheel'],
    project_urls={
        'Documentation': 'https://home.undefinedlabs.com/goto/python-agent',
        'Source': 'https://github.com/undefinedlabs/scope-go-agent',
        'Tracker': 'https://github.com/undefinedlabs/scope-go-agent/issues',
    },
)
