from setuptools import setup, Extension
from Cython.Distutils import build_ext
import numpy as np

NAME = "hse-search"
VERSION = "0.0.1"
DESCR = "!"
REQUIRES = [
    'numpy', 
    'cython',
    'google-cloud-storage==1.19.1',
    'google-cloud-bigtable',
    'gensim',
    'cachetools'
]

AUTHOR = "Mark Hudson"
EMAIL = "mark.cd.hudson@gmail.com"

LICENSE = "Apache 2.0"

SRC_DIR = "hse_search"
PACKAGES = [SRC_DIR, SRC_DIR + ".low_level", SRC_DIR + ".query_components"]

ext_1 = Extension(SRC_DIR + ".low_level.wrapped",
                  [SRC_DIR + "/low_level/wrapped.pyx"],
                  libraries=[],
                  include_dirs=[np.get_include()])


EXTENSIONS = [ext_1]

if __name__ == "__main__":
    setup(install_requires=REQUIRES,
          packages=PACKAGES,
          zip_safe=False,
          name=NAME,
          version=VERSION,
          description=DESCR,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          cmdclass={"build_ext": build_ext},
          ext_modules=EXTENSIONS
          )
