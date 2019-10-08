"""Setup for the fastai splunk package."""

import setuptools


with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Nate Argroves",
    author_email="nargroves@gmail.com",
    name='fastai-splunk',
    license="Apache Software License 2.0",
    description='fastai-splunk allows you to import Splunk data using fastai',
    version='v0.0.1',
    long_description=README,
    url='https://github.com/nargroves/fastai-splunk',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['fastai','splunk-sdk'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
