from setuptools import setup, find_packages

with open("README.md") as fh:
    long_description = fh.read()
    
if __name__ == '__main__':
    setup(name = 'bhcd',
          version = '0.3.post1',
          description = 'Bayesian Hierarchical Community Discovery',
          author = 'zhaofeng-shu33',
          install_requires = ['pybhcd'],
          author_email = '616545598@qq.com',
          url = 'https://github.com/zhaofeng-shu33/bhcd-python-wrapper',
          maintainer = 'zhaofeng-shu33',
          maintainer_email = '616545598@qq.com',
          long_description = long_description,
          long_description_content_type="text/markdown",
          license = 'Apache License Version 2.0',
          packages = find_packages(),
          classifiers = (
              "Development Status :: 4 - Beta",
              "Programming Language :: Python :: 3.7",
              "Programming Language :: Python :: 3.6",
              "Operating System :: OS Independent",
          ),
    )
