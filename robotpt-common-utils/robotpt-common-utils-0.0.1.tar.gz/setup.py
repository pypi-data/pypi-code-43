from distutils.core import setup


setup(
  name='robotpt-common-utils',
  packages=['robotpt_common_utils'],
  version='0.0.1',
  license='MIT',
  description='Common python functions used in RobotPT projects',
  author='Audrow Nash',
  author_email='audrowna@usc.edu',
  url='https://github.com/robotpt/robotpt-common-utils',
  setup_requires=[
    'wheel',
  ],
  install_requires=[
    'pandas',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
  ],
)
