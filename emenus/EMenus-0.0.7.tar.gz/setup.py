from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()
setup(
    name='EMenus',
    version='0.0.7',
    description='a simpler way to create menus!',
    license='MIT',
    packages=['EMenus'],
    author='Artur Zaytsev',
    author_email='huskielunar@gmail.com',
    keywords=['menus','easier','Artur Zaytsev','EMenus'],
    url='https://github.com/HUSKI3/EMenus',
    long_description=long_description,
    long_description_content_type='text/markdown'
)