import os
import re
from setuptools import setup, find_packages


RE_PY_VERSION = re.compile(
    r'__version__\s*=\s*["\']'
    r'(?P<version>\d+(\.\d+(\.\d+)?)?)'
    r'["\']'
)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_version():
    content = read('src/scaffy/__init__.py')
    m = RE_PY_VERSION.search(content)
    if not m:
        return '0.0'
    else:
        return m.group('version')


setup(
    name="scaffy",
    version=read_version(),
    author="Mateusz 'novo' Klos",
    author_email="novopl@gmail.com",
    license="MIT",
    keywords="project scaffold dev tools",
    url="http://github.com/novopl/scaffy",
    description="Set of CLI commands for project scaffolds",
    long_description=read('README.rst'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'cached-property~=1.4.3',
        'click~=7.0',
        'pyyaml~=5.1.2',
        'six~=1.12.0',
        'requests~=2.22.0',
    ],
    entry_points={
        'console_scripts': [
            'scaffy = scaffy.main:cli',
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
