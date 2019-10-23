# coding: utf-8
import codecs

from setuptools import setup, find_packages

package_name = "vii-sdk"

exec(open("vii_sdk/version.py").read())

with codecs.open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

tests_require = ['pytest', 'mock']

requirements_file = 'requirements.txt'

setup(
    name=package_name,
    version=__version__,
    description='Code for managing vii.vip blockchain transactions and accounts using vii_sdk in python. Allows full functionality interfacing with the Horizon front end. Visit https://vii.vip for more information.',
    long_description=long_description,
    keywords=["vii.vip", "blockchain", "distributed exchange", "cryptocurrency", "dex", "sdex", "trading"],
    license='Apache',
    author='VII',
    author_email='admin@vii.vip',
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=open(requirements_file).readlines(),
    tests_require=tests_require
)
