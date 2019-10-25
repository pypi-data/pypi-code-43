from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='gabid',
      version='0.6',
      description='Gaussian and Binomial distributions',
      packages=['gabid'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Sara Garci',
      author_email='s@saragarci.com',
      zip_safe=False)
