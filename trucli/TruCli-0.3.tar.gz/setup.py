from distutils.core import setup
setup(
  name = 'TruCli',         # How you named your package folder (MyLib)
  packages = ['TruCli'],   # Chose the same as "name"
  version = '0.3',      # Start with a small number and increase it with every change you make
  license='GNU GPLv3',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A small library to create CLIs fully contained in Python',   # Give a short desscription about your library
  author = 'Filippo De Angelis',                   # Type in your name
  author_email = 'filippodeangelis0@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/FilippoDeAngelis/TruCli',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/FilippoDeAngelis/TruCli/archive/v0.3.tar.gz',
  keywords = ['CLI', 'CONTAINER', 'INSIDE'],
  install_requires = [
    'typing'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   # Again, pick a license
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)