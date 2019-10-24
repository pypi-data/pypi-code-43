from setuptools import setup,find_packages

VERSION = '0.0.1'

setup(name='ydt',
      version=VERSION,
      description="a command line tool for simple translation from zd to en",
      long_description='a command line tool for simple translation from zd to en',
      classifiers=[],
      keywords='ydt',
      author='Wu Lianwei',
      author_email='maxwupro@outlook.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points={
          'console_scripts': [
              'ydt = ydt.ydt:get_info'
          ]
      }
      )
