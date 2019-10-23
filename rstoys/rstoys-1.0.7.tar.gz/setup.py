import setuptools

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setuptools.setup(
    name='rstoys',
    version='1.0.7',
    description='Library for simple real-time control of robotic toys.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/rstechnology/rstoys/src/master/',
    author='Radek Szamrej',
    author_email='rstechnology@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    zip_safe=False)
