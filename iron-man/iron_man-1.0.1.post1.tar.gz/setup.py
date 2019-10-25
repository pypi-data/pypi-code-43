# -*- coding: utf-8 -*-
# @Time    : 2019-05-29 10:42
# @E-Mail  : wujifan1106@gmail.com
# @Site    : 
# @File    : setup.py
# @Software: PyCharm
import os
# from distutils.core import setup
from setuptools import setup
# here = os.path.abspath(os.path.dirname(__file__))

ext_files = [os.path.join("iron_man", "c_bloomfilter.c")]

kwargs = {}

from Cython.Distutils import build_ext
from Cython.Distutils import Extension

print('Building from Cython')
ext_files.append(os.path.join("iron_man", "py_bloomfilter.pyx"))
# ext_files.append("./bloomfilter/py_bloomfilter.pyx")
kwargs['cmdclass'] = {'build_ext': build_ext}

ext_modules = [Extension("CBloomfilter", ext_files)]
# ext_modules = cythonize(ext_files[0])
about = {}
with open(os.path.join('iron_man', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

from os import path as os_path

this_directory = os_path.abspath(os_path.dirname(__file__))


def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


setup(
    name=about['__title__'],
    version=about['__version__'],
    url=about['__url__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    license=about['__license__'],
    ext_modules=ext_modules,
    # py_modules=['bloomfilter.__init__'],
    packages=['iron_man'],
    package_dir={
        'iron_man': "iron_man"
    },
    package_data={
        '': ['LICENSE', 'NOTICE'],
        "iron_man": ["c_bloomfilter.h", "bloomfilter.c_bloomfilter.h"]
    },
    # include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Cython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    **kwargs
)
