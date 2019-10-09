from setuptools import setup, find_packages
setup(
      #name ="main" name = "edict"
      name="edict",
      version = "0.51",
      description="handle dict,nested Dict,APIs",
      author="dapeli",
      #https://github.com/ihgazni2/main
      url="https://github.com/ihgazni2/edict",
      author_email='terryinzaghi@163.com', 
      license="MIT",
      #refer to .md files in https://github.com/ihgazni2/main 
      long_description = "refer to .md files in https://github.com/ihgazni2/edict",
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      #py_modules=['main']
      py_modules=['edict'], 
      )


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist

