from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='examplepkgjanewilliams',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['examplepkgjanewilliams'],
      zip_safe=False)
