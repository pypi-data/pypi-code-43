import sys

from setuptools import setup

if sys.version_info >= (3, 0, 0):
    msg = 'This is supposed to be used only with Python 2. Found version %s' % sys.version
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

line = 'z5'
version = get_version(filename='src/zuper_nodes_python2/__init__.py')

setup(
        name='zuper-nodes-python2-%s' % line,
        version=version,
        keywords='',
        package_dir={'': 'src'},
        packages=[
            'zuper_nodes_python2',
        ],
        install_requires=[
            'cbor2',
        ],

)
