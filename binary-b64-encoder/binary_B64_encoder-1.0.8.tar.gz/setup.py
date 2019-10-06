# -*- coding: utf-8 -*-
"""binary_B64_encoder module can be installed and configured from here"""



import json
from os import path
from setuptools import setup, find_packages
from sys import version_info

VERSION = "1.0.8"
CURR_PATH = "{}{}".format(path.abspath(path.dirname(__file__)), '/')




def path_format(file_path=None, file_name=None, is_abspath=False,
                ignore_raises=False):
    """
    Get path joined checking before if path and filepath exist,
     if not, raise an Exception
     if ignore_raise it's enabled, then file_path must include '/' at end lane
    """
    path_formatted = "{}{}".format(file_path, file_name)
    if ignore_raises:
        return path_formatted
    if file_path is None or not path.exists(file_path):
        raise IOError("Path '{}' doesn't exists".format(file_path))
    if file_name is None or not path.exists(path_formatted):
        raise IOError(
            "File '{}{}' doesn't exists".format(file_path, file_name))
    if is_abspath:
        return path.abspath(path.join(file_path, file_name))
    else:
        return path.join(file_path, file_name)


def read_file(is_json=False, file_path=None, encoding='utf-8',
              is_encoding=True, ignore_raises=False):
    """Returns file object from file_path,
       compatible with all py versiones
    optionals:
      can be use to return dict from json path
      can modify encoding used to obtain file
    """
    text = None
    try:
        if file_path is None:
            raise Exception("File path received it's None")
        if version_info.major >= 3:
            if not is_encoding:
                encoding = None
            with open(file_path, encoding=encoding) as buff:
                text = buff.read()
        if version_info.major <= 2:
            with open(file_path) as buff:
                if is_encoding:
                    text = buff.read().decode(encoding)
                else:
                    text = buff.read()
        if is_json:
            return json.loads(text)
    except Exception as err:
        if not ignore_raises:
            raise Exception(err)
    return text


def read(file_name=None, is_encoding=True, ignore_raises=False):
    """Read file"""
    if file_name is None:
        raise Exception("File name not provided")
    if ignore_raises:
        try:
            return read_file(
                is_encoding=is_encoding,
                file_path=path_format(
                    file_path=CURR_PATH,
                    file_name=file_name,
                    ignore_raises=ignore_raises))
        except Exception:
            # TODO: not silence like this,
            # must be on setup.cfg, README path
            return 'NOTFOUND'
    return read_file(is_encoding=is_encoding,
                     file_path=path_format(
                         file_path=CURR_PATH,
                         file_name=file_name,
                         ignore_raises=ignore_raises))


setup(
    name='binary_B64_encoder',
    version=VERSION,
    license=read("LICENSE", is_encoding=False, ignore_raises=True),
    packages=find_packages(),
    description='This script encode the binary input file to base64',
    long_description_content_type='text/markdown',
    long_description=read("README.md"),
    author='Gerardo G. Urtiaga ',
    author_email='gerardo.garcia.urtiaga@gmail.com',
    url='https://github.com/gerardogu/binary-B64-encoder',
    download_url='https://github.com/gerardogu/binary-B64-encoder/tarball/{version}'.format(
        version=VERSION),
    keywords=['b64encode', 'base 64', 'b64', 'binary_B64_encoder', 'file base64'],
    install_requires=[
        'argparse',
    ],
    setup_requires=['argparse'],
    tests_require=[
        'pytest==3.9.3',
        'pytest-cov',
        'pytest-html',
        'pytest-dependency',
    ],
    entry_points={
        'console_scripts': ['b64encode=binary_B64_encoder.b64encode:main'],
    },
    #classifiers=[
        #'Development Status :: 4 - Beta',
        #'Intended Audience :: Developers',
        #'Topic :: Software Development :: Build Tools',
        #'Programming Language :: Python :: 2.7',
    #],
)
