"""
sceleton

Usage:
  sceleton new [packagename] [--django] [--virtualenv | --venv] [--quick]
  sceleton init [--path=path] [--quick]
  sceleton module [modulename] [--parentmodule=parentmodule] [--add] [files]
  sceleton add [package(s)]
  sceleton install [package(s)] [--no-add]
  sceleton remove [package(s)]
  sceleton classifiers [--edit]
  sceleton user [--edit]
  sceleton license [--edit]
  sceleton keywords [--edit]
  sceleton build
  sceleton upload
  sceleton local

  sceleton -h | --help
  sceleton -v | --version

Options:
  new [packagename] [--virtualenv | --venv] [--django] [--quick] 
                Creates a new package, with [packagename] if file with 
                given name doesn't exist, or sets a new django project, if `--django` is used.
                By default doesn't initializes a virtual environment, which can be 
                changed by givin one of the
                options `--virtualenv` or `--venv`. /it uses the python's venv package`
                If you give the option `--quick`, it will not ask for any 
                questions, and will create the project folder.
                For non django project, files included in the final folder are:
                  - .gitignore
                  - setup.py
                  - LICENSE
                  - README.rst
                  - project folder, and __init__ file
                  - setup.cfg
                In a djagno project, creates only README.rst, LICENSE, .gitignore
                
  init [--path=path] [--quick] Creates only a setup.py file, 
                               in the current path, 
                               if `--path` option is not given. 
                               If `--quick` is given, will not ask any
                               question, and will make basic `setup.py` file.

  add [package(s)]          Adds one or more packages 
                            (separated with intervals) 
                            to the setup.py file, 
                            without installing them

  install [packages(s)] [--no-add]    If list of packages is given 
                            (separated with intervals) 
                            will install all of them, and
                            will add them to setup.py file, 
                            except if `--no-add` option is given

  remove [package(s)]       Removes a package, or list 
                            of packages from setup.py. 
                            It doesn't uninstall them.

  classifiers [--edit]      Without arguments, will list all current 
                            classifiers in the setup.py file. If `--edit` is
                            given, will ask the user for new classifiers, erasing
                            the old one.

  user [--edit]             Shows the user's name and email, inserted in the
                            `setup.py` file. If `--edit` is provided, it will
                            change those fields, with the new one, given
                            by the user.

  license [--edit]          If no `--edit` option is given, will show the current
                            LICESENSE. If `--edit` is given, it will show to the user
                            all possible licenses, and when choosing a new one, will
                            create a new LICESENSE file.

  build                     Builds the project using 
                            `python setup.py sdist` command

  upload                    Uploads the project, using 
                            `twine upload dist/*` command
  
  local                     Installs the package locally, using 
                            the command `python setup.py install`

Other options:
  -h --help  shows possible commands.
  -v --version  shows current version of the package.
Help:
  For suggestions/problems and etc. visit the github reposityory https://github.com/monzita/sceleton
"""
import sys

from docopt import docopt

from .decorators.subargs import subargs
from . import command


VERSION = '0.0.1'

@subargs(sys_args=sys.argv)
def main(*args, **kwargs):
  global VERSION

  sys.argv = args
  if len(sys.argv) < 2:
    docopt(__doc__, version=VERSION)
    return

  options = docopt(__doc__, version=VERSION)

  kwargs.update(options)
  command.exec(*args, **kwargs)
