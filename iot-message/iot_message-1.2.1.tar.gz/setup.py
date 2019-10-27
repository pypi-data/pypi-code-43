# -*- coding: utf-8 -*-

"""setup for IOT Message package"""

import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as file_handler:
        return file_handler.read()

setup(
    name='iot_message',
    version='1.2.1',
    description='Custom iot:1 protocol',
    keywords=['iot:1'],
    long_description=(read('README.rst')),
    url='https://github.com/bkosciow/python_iot-1',
    license='MIT',
    author='Bartosz Kościów',
    author_email='kosci1@gmail.com',
    py_modules=['iot_message'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Home Automation'
    ],
    packages=find_packages(exclude=['tests*']),
)
