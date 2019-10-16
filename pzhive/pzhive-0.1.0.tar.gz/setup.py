from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pzhive',
    version='0.1.0',
    packages=['pzhive'],
    url='https://github.com/AngersZhuuu/pzhive',
    license='',
    author='anegrszhuuu',
    author_email='angers.zhu@gmail.com',
    long_description=long_description,
    long_description_content_type="markdown",
    description='',
)
