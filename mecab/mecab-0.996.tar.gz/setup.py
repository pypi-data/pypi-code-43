#!/usr/bin/env python
from codecs import open
import os
import platform
from setuptools import setup, Extension
import sys


def cmd1(strings):
    return os.popen(strings).readlines()[0].rstrip()


def cmd2(strings):
    return cmd1(strings).split()


if platform.system() == 'Windows':
    if sys.maxsize > 2**32:  # 64bit
        ext_modules = [
            Extension(
                "_MeCab",
                ["MeCab_wrap.cxx"],
                library_dirs=[r"C:\Program Files\MeCab\sdk"],
                libraries=["libmecab"]
            )
        ]
        data_files = [(r'lib\site-packages', [r"C:\Program Files\MeCab\\bin\libmecab.dll"])]
    else:  # 32bit
        ext_modules = [
            Extension(
                "_MeCab",
                ["MeCab_wrap.cxx",],
                library_dirs=[r"C:\Program Files (x86)\MeCab\sdk"],
                libraries=["libmecab"]
            )
        ]
        data_files = [(r'lib\site-packages', [r"C:\Program Files (x86)\MeCab\bin\libmecab.dll"])]
else:
    ext_modules=[
        Extension(
            "_MeCab",
            ["MeCab_wrap.cxx"],
            include_dirs=cmd2("mecab-config --inc-dir"),
            library_dirs=cmd2("mecab-config --libs-only-L"),
            libraries=cmd2("mecab-config --libs-only-l"))
    ]
    data_files = None

setup(
    name="mecab",
    version="0.996",
    py_modules=["MeCab"],
    ext_modules=ext_modules,
    data_files=data_files,
    author='Yukino Ikegami',
    author_email='yknikgm@gmail.com',
    url='https://github.com/ikegami-yukino/mecab/tree/master/mecab/python',
    license='BSD, GPL or LGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing'
    ],
    description='MeCab binding for many OSs (Windows, macOS, and Linux)',
    long_description=open('README.rst', encoding='utf8').read(),
    long_description_content_type='text/x-rst'
)