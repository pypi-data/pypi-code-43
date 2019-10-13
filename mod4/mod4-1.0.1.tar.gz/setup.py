from setuptools import setup

def readme():
  with open("README.md", "r") as fh:
      README = fh.read()
  return README

setup(
       name='mod4',
       version='1.0.1',
       long_description=readme(),
       long_description_content_type="text/markdown",
       py_modules=['mod4'],
       license='MIT',
       author='ziejaCode',
       author_email='czarny25101@gmail.com',       
       url='https://github.com/czarny25/mod3.git',
       description="Test class for study"
     )