from setuptools import setup, find_packages


with open("README.md", "r") as fh:
        long_description = fh.read()

setup(name='poolmanager',
      version='0.1.0',
      description='Simple pool manager',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering :: GIS',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords='',
      author='Loic Gasser',
      author_email='loicgasser4@gmail.com',
      license='MIT',
      url='https://github.com/geoadmin/lib-poolmanager',
      packages=find_packages(exclude=['tests']),
      package_dir={'poolmanager': 'poolmanager'},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[],
      )
