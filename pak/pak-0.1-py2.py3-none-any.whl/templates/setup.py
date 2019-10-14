from setuptools import setup, find_packages
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='${app}',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='${description}',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='${author}',
      author_email='${email}',
      url='${url}',
      packages=find_packages(exclude=["tests"]),
      # tox added so makefile targets work out of the box
      install_requires=["tox"],
      entry_points={
          'console_scripts': ['${app}=${app}.main:main']
      },
      package_data={
          '${app}': ['${app}/${package_data}']
      },
      include_package_data=True,
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'Operating System :: POSIX',
                   'Operating System :: MacOS :: MacOS X',
                   'Programming Language :: Python :: 3'])
