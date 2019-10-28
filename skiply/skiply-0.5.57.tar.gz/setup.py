from setuptools import setup, find_packages

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name='skiply',
	version='0.5.57',
	description='Skiply Library',
	url='https://github.com/skiplyfrance/skiply.git',
	author='Caroline Bouchat',
	author_email='caroline@skiply.fr',
    packages=find_packages(),
    namespace_packages=['skiply'],
	zip_safe=False)