from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='compare_for_testing',
    version='1.0',
    packages=find_packages(),
    author='vaindante',
    author_email='vaindante@gmail.ru',
    url='https://github.com/vaindante/compare_for_testing',
    long_description=open(join(dirname(__file__), 'Readme.txt')).read(),
    include_package_data=True,
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
