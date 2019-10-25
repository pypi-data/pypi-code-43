from setuptools import setup, find_packages


requirements = []

setup(
      name="efuntool",
      version = "0.0.72", #@version@#
      description="handle,.in progressing..,APIs",
      author="ihgazni2",
      url="https://github.com/ihgazni2/efuntool",
      author_email='', 
      license="MIT",
      long_description = "refer to .md files in https://github.com/ihgazni2/efuntool",
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      entry_points={
          'console_scripts': [
              'efuntool=efuntool.bin:main'
          ]
      },
      package_data={
          'resources':['RESOURCES/*']
      },
      include_package_data=True,
      install_requires=requirements,
      py_modules=['efuntool'], 
)


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist





































































