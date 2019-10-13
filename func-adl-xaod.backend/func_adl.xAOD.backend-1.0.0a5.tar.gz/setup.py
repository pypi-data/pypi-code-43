from setuptools import find_namespace_packages
from distutils.core import setup
from os import listdir

# Use the readme as the long description.
with open("README.md", "r") as fh:
    long_description = fh.read()

xaod_template_files = listdir('func_adl/xAOD/backend/R21Code')
with open('C:/Users/gordo/Documents/Code/IRIS-HEP/func_adl.xAOD.backend/setuplog.out', 'w') as o:
    o.write(str(xaod_template_files) + '\n')
    o.write(str(find_namespace_packages(exclude=['tests'])) + '\n')
setup(name="func_adl.xAOD.backend",
      version='1.0.0-alpha.5',
      packages=['func_adl.xAOD.backend'] + [f'func_adl.xAOD.backend.{f}' for f in ['ast', 'cpplib', 'dataset_resolvers', 'xAODlib']],
      scripts=[],
      description="Functional Analysis Description Language for xAOD backends",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="G. Watts (IRIS-HEP/UW Seattle)",
      author_email="gwatts@uw.edu",
      maintainer="Gordon Watts (IRIS-HEP/UW Seattle)",
      maintainer_email="gwatts@uw.edu",
      url="https://github.com/iris-hep/func_adl.xAOD.backend",
      license="TBD",
      test_suite="tests",
      install_requires=["requests>=2.0.0", "pandas>=0.24.0", "uproot>=3.7.0", "retry>=0.9.2", "Jinja2>=2.10", "func_adl.xAOD==1.0.0a4"],
      setup_requires=["pytest-runner"],
      tests_require=["pytest>=3.9"],
      classifiers=[
                   # "Development Status :: 1 - Planning",
                   "Development Status :: 2 - Pre-Alpha",
                   # "Development Status :: 3 - Alpha",
                   # "Development Status :: 4 - Beta",
                   # "Development Status :: 5 - Production/Stable",
                   # "Development Status :: 6 - Mature",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Information Technology",
                   "Programming Language :: Python",
                   "Topic :: Software Development",
                   "Topic :: Utilities",
      ],
      data_files=[('func_adl/xAOD/backend/R21Code', [f'func_adl/xAOD/backend/R21Code/{f}' for f in xaod_template_files])],
      platforms="Any",
      )
