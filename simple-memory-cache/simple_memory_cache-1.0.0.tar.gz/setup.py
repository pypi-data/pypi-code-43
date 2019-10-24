from setuptools import setup

from os import path
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name='simple_memory_cache',
    version='1.0.0',
    description='Dead Simple Memory Cache',
    url='https://gitlab.com/tackv/simple-memory-cache',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='William Laroche',
    author_email='william.laroche@tackv.ca',
    maintainer='William Laroche',
    maintainer_email='william.laroche@tackv.ca',
    py_modules=['simple_memory_cache'],
    package_data={
    },
    install_requires=[
    ],
    extras_require={
    },
    setup_requires=[
    ],
    tests_require=[
        'pytest',
        'pytest-cov'
    ],
    test_suite="pytest",
)