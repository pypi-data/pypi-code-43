from setuptools import setup

import sys

if not sys.version_info >= (3, 6, 0):
    msg = 'Unsupported version %s' % sys.version
    raise Exception(msg)


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='src/zuper_nodes/__init__.py')
line = 'z5'
setup(
        name=f'zuper-nodes-{line}',
        version=version,
        keywords='',
        package_dir={'': 'src'},
        packages=[
            'zuper_nodes',
            'zuper_nodes_tests',
            'zuper_nodes_wrapper',
            'zuper_nodes_wrapper_tests',
        ],
        install_requires=[
            'compmake',
            'pyparsing',
            'PyContracts',
            'networkx',
            'termcolor',
            'zuper-ipce-z5',
            'cbor2',
            'base58',
        ],
        entry_points={
            'console_scripts': [
                'zuper-node-identify=zuper_nodes_wrapper.identify:identify_main',
            ],
        },
)
