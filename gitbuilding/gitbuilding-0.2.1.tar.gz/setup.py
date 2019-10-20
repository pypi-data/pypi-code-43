 
__author__ = 'Julian Stirling'

from setuptools import setup, find_packages
import sys
from os import path
import glob

if sys.version_info[0] == 2:
    sys.exit("Sorry, Python 2 is not supported")

#Globbing all of the static files and then removing `gitbuilding/` from the start
package_data_location = glob.glob('gitbuilding/static/**/*', recursive=True)
package_data_location = [package[12:] for package in package_data_location]

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name = 'gitbuilding',
      version = '0.2.1',
      description = 'For documenting and open source hardware project with minimal effort, so you can stop writing and git building.',
      long_description = long_description,
      long_description_content_type='text/markdown',
      author = 'Julian Stirling',
      author_email = 'julian@julianstirling.co.uk',
      packages = find_packages(),
      
      package_data={'gitbuilding': package_data_location},
      keywords = ['Documentation','Hardware'],
      zip_safe = True,
      url = 'https://gitlab.com/bath_open_instrumentation_group/git-building',
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3.6'
          ],
      install_requires=['argparse','regex','pyyaml>=5.1','flask','requests','markdown','colorama'],
      python_requires=">=3.6",
      entry_points = {'console_scripts': ['gitbuilding = gitbuilding.__main__:main']},
      )

