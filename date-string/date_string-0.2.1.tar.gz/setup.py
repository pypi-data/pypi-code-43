# coding=utf-8

from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='date_string',
    version=__import__('date_string').__version__,
    description="Creates a manipulable date string in the form of 'YYYYmmdd'.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='WeiJi Hsiao',
    license='MIT License',
    packages=['date_string'],
)
