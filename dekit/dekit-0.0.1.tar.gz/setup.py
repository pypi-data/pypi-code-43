from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='dekit',
    version='0.0.1',
    description='A collection of useful Python decorators',
    long_description=readme,
    long_description_content_type="text/x-rst",
    author='Kaitian Xie',
    author_email='xkaitian@gmail.com',
    url='https://github.com/algobot76/dekit',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs'))
)
