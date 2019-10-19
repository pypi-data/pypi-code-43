from distutils.core import setup
setup(
  name = 'helper_functions_007',         # How you named your package folder (MyLib)
  packages = ['helper_functions_007'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'This module provides a handful of functions to simplify the typical data processing operations and simplifying data verification procedures.',   # Give a short description about your library
  author = 'Victor Popov',                   # Type in your name
  author_email = 'victorvtf@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/v-popov/helper_funcs',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/v-popov/helper_funcs/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['Helper', 'Functions', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'numpy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
  ],
)