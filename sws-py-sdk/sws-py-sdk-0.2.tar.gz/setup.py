import setuptools
setuptools.setup(
  name = 'sws-py-sdk',         # How you named your package folder
  packages = ['sws_py_sdk'],   # Choose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A Python SDK for managing communication with SWS APIs',   # Give a short description about your library
  author = 'Benjamin Farrelly',
  author_email = 'benjamin.farrelly@serato.com',
  url = 'https://github.com/user/serato',
  download_url = 'https://github.com/serato/sws-py-sdk/archive/v0.1.0.tar.gz',
  keywords = ['Serato', 'API', 'SDK'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7'
  ],
  python_requires='>=3.6',
  install_requires=[
    'requests',
    'requests-mock',
    'pytest'
  ]
)