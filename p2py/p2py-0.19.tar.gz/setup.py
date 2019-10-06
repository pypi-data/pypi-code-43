from distutils.core import setup
setup(
  name = 'p2py',         # How you named your package folder (MyLib)
  packages = ['p2py'],   # Chose the same as "name"
  version = '0.19',      # Start with a small number and increase it with every change you make
  license='AGPLv3',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'The simplest peer to peer networking Python library',   # Give a short description about your library
  author = 'Adam Szokalski',                   # Type in your name
  author_email = 'aszokalski@ipds.team',      # Type in your E-Mail
  url = 'https://github.com/ipds/p2py',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/ipds/p2py/archive/0.1.tar.gz',    # I explain this later on
  keywords = ['p2p', 'peer', 'networking', 'simple'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'colorlog',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',    'License :: OSI Approved :: GNU Affero General Public License v3',   # Again, pick a license    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)