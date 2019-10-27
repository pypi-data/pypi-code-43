from os.path import dirname, join

from setuptools import setup

import pm4pycvxopt


def read_file(filename):
    with open(join(dirname(__file__), filename)) as f:
        return f.read()


setup(
    name=pm4pycvxopt.__name__,
    version=pm4pycvxopt.__version__,
    description=pm4pycvxopt.__doc__.strip(),
    long_description=read_file('README.md'),
    author=pm4pycvxopt.__author__,
    author_email=pm4pycvxopt.__author_email__,
    py_modules=[pm4pycvxopt.__name__],
    include_package_data=True,
    packages=['pm4pycvxopt', 'pm4pycvxopt.util', 'pm4pycvxopt.util.lp', 'pm4pycvxopt.util.lp.versions'],
    url='http://www.pm4py.org',
    license='GPL 3.0',
    install_requires=[
        'pm4py',
        'cvxopt'
    ],
    project_urls={
        'Documentation': 'http://pm4py.pads.rwth-aachen.de/documentation/',
        'Source': 'https://github.com/pm4py/pm4py-source',
        'Tracker': 'https://github.com/pm4py/pm4py-source/issues',
    }
)
