from distutils.core import setup
setup(
  name = 'zinobe-dates',
  packages = ['zinobe'],
  version = '0.2.1',
  license='MIT',
  description = 'get last day of pay for periods, if is a holidays take a next business day',
  author = 'Zinobe',
  author_email = 'dylan.cipagauta@zinobe.com',
  url = 'https://github.com/DylanZinobe/Dates',
  download_url = 'https://github.com/DylanZinobe/Dates/archive/0.2.tar.gz',
  keywords = ['zinobe', 'dates'],
  install_requires=[
          'numpy',
          'holidays',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)