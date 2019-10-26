#!/usr/bin/env python
from distutils.core import setup
from winpid.version import release

setup(name='winpid',
      version=release,
      description='Create pid file and remove at exit',
      long_description="""Does not require fnctl and works on both Windows and Linux""",
      author='László Zsolt Nagy',
      author_email='nagylzs@gmail.com',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      install_requires=[],
      requires=['psutil'],
      url="https://github.com/nagylzs/winpid",
      classifiers=[
          "Topic :: Utilities",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: Implementation :: CPython",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: Unix",
      ],
      )
