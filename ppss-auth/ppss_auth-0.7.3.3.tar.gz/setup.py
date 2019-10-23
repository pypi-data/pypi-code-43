from setuptools import setup,find_packages


import os
here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.md'), 'r').read()
changelog = open(os.path.join(here, 'README.md'), 'r').read()

setup(name='ppss_auth',
  version='0.7.3.3',
  description='simple auth scheme for pyramid, based on Mako template and sqlalchemy backend',
  long_description=readme + "\n\n\n" + changelog,
  long_description_content_type="text/markdown",
  author='pdepmcp',
  author_email='d.cariboni@pingpongstars.it',
  license='MIT',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 2.7',
  ],
  keywords="pyramid module authentication accelerator",
  python_requires='>=2.7',
  url='http://www.pingpongstars.it',
  install_requires=['pyramid_mako','pyramid_beaker' ],
  #packages=['src/test1'],
  packages=find_packages(),
  include_package_data=True,

)


