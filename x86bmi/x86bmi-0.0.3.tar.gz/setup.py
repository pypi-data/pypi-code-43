import setuptools
#from setuptools import Extension

import os

### https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives

# rm -r dist; python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*

### pip3 install twine
### python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

d0 = os.path.dirname(os.path.abspath(__file__))
os.system('cd "%s/pkg"; make' % d0)

#cmod = Extension(
  #'bmi_intrin', 
  #sources = ['pkg/bmi_intrin.c'], 
  #language='c', 
  #extra_compile_args = '-O3 -mbmi -mbmi2 -mpopcnt -mlzcnt -mtune=native'.split()
#)

pkgs = setuptools.find_packages()

setuptools.setup(
  name="x86bmi",
  version="0.0.3",
  author="noname00",
  author_email="author@example.com",
  description="x86 intrin for bmi instructions",
  long_description="",
  #long_description_content_type="text/markdown",
  #url="https://github.com/pypa/sampleproject",
  packages=pkgs,
  package_data={p: ['makefile', '*.c', '*.so'] for p in pkgs},
  classifiers=[
    "Programming Language :: Python :: 3",
    #"License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6',
  install_requires=['numpy'], 
  #ext_modules = [cmod],
)
