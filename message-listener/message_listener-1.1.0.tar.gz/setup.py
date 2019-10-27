# -*- coding: utf-8 -*-

"""setup for message_listener package"""

import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as file_handler:
        return file_handler.read()

setup(
    name='message_listener',
    version='1.1.0',
    description='Server listener and iot_message handler',
    keywords=['iot_message', 'raspberry pi'],
    long_description=(read('README.rst')),
    url='https://github.com/bkosciow/message_listener',
    license='MIT',
    author='Bartosz Kościów',
    author_email='kosci1@gmail.com',
    py_modules=['message_listener'],
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
    install_requires=[
        'iot_message',
    ],
    packages=find_packages(exclude=['tests*']),
)
