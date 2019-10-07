from setuptools import setup, find_packages
setup(
      name="elist",
      version = "0.4.53",
      description="handle list,nested list tree",
      author="dapeli",
      url="https://github.com/ihgazni2/elist",
      author_email='terryinzaghi@163.com', 
      license="MIT",
      long_description = "refer to .md files in https://github.com/ihgazni2/elist",
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      py_modules=['elist'], 
      )


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist

