from setuptools import setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(
  name = 'helper_funcs',         # How you named your package folder (MyLib)
  long_description=long_description,
  long_description_content_type='text/markdown',
  packages = ['helper_funcs'],   # Chose the same as "name"
  version = '0.1.3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'This module provides a handful of functions to simplify the typical data processing operations and simplifying data verification procedures.',   # Give a short description about your library
  author = 'Victor Popov',                   # Type in your name
  author_email = 'victorvtf@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/v-popov/helper_funcs',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/v-popov/helper_funcs/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['Helper', 'Functions', 'Data Science'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'numpy',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
  ],
)