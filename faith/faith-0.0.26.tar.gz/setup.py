from setuptools import find_packages
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='faith',
    version='0.0.26',
    author='Thomas Wang',
    author_email='w@datability.io',
    description='the faith API for investment portfolio management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/datability-io/faith',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'asciitree==0.3.3',
        'pytz==2019.2',
        'redis==3.3.8',
        'requests==2.22.0',
        'termcolor==1.1.0',
        'terminaltables==3.1.0',
    ],
    package_data={'faith': ['py.typed']},
)
