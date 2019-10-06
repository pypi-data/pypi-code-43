from setuptools import setup

with open('README.txt') as f:
    long_description = f.read()

setup(name='palora',
      version='3.1',
      description='Wrapper Class around cx_Oracle for Oracle Autonomous Database',
      long_description=long_description,
      url='https://github.com/ipal0/palora',
      author='Pal',
      author_email='ipal00@outlook.com',
      license='GPL',
      install_requires=[ 'cx_Oracle', ],
      python_requires='>=3',
      packages=['palora'])
