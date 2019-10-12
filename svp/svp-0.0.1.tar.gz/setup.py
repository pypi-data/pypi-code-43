from distutils.core import setup
setup(
  name = 'svp',
  packages = ['svp'],
  version = '0.0.1',
  license='MIT',
  description = 'SVP - A lightweight API testing microframework.',
  author = 'josh.grant',
  author_email = 'josh.grant@saucelabs.com',
  url = 'https://github.com/joshmgrant/svp/',
  download_url = 'https://github.com/joshmgrant/svp/archive/v_001.tar.gz', # based on GitHub releases
  keywords = ['api', 'testing', 'requests'],
  install_requires=[
          'requests',
          'pytest'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Testing',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
