# /usr/bin/env python3

from functools import lru_cache
from pathlib import Path
from shutil import rmtree

from setuptools import Command
from setuptools import find_packages
from setuptools import setup

PROJECT_NAME = 'dfmpy'
PROJECT_VERSION = '0.0.0'


def get_repo_file(*args):
    """
    Joins all the arguments into a single string that will be normalized into an
    absolute file path.  Essentially the path will point to a file within this
    repository.

    :param args: Names to join that make up a relative file path.

    :rtype: Path
    :return: The absolute path to a file within this repository.
    """
    return Path(__file__).resolve().parent.joinpath(*args)


@lru_cache(maxsize=2)
def read_file(filename):
    """
    Reads the specified file and returns the full contents as a single string.

    :param filename: The file to read.

    :rtype: str
    :return: The full contents of the specified file.
    """
    with open(filename) as f:
        return f.read()


def get_dfmpy_packages():
    """
    Finds all packages within this project and only returns the production ready
    ones.  Meaning, test packages will not be included.

    :rtype tuple
    :return: A sequence of package names that will be built into the file
            distribution.
    """
    packages = find_packages()
    packages = [p for p in packages if not p.endswith('_test')]
    return tuple(packages)


def load_requirements(filename):
    """
    Loads the :code:`requirements.tx` dependency file and returns the
    dependencies as a sequence.

    The file can contain comments that follow the pound symbol (eg. '#').
    Comments will be removed, each line is stripped of leading and trailing
    whitespace, and empty lines are deleted.  Other than these basic
    transformations, the requirements are left intact.

    :param str filename: The requirements file to read.

    :rtype: tuple
    :return: A sequence of requirements.
    """
    reqs = read_file(filename).splitlines()
    reqs = [str(x).strip() for x in reqs]
    reqs = [x[:x.find('#')] for x in reqs if '#' in x]
    reqs = [x for x in reqs if len(x)]
    return tuple(reqs)


class CleanCommand(Command):
    """
    A custom clean command that removes any intermediate build directories.
    """

    description = 'Custom clean command that forcefully removes build, dist,' \
                  ' and other similar directories.'
    user_options = []

    def __init__(self, *args, **kwargs):
        """Initialized the custom clean command with a list of directories."""
        super(CleanCommand, self).__init__(*args, **kwargs)
        project_path = Path(__file__).resolve().parent
        self._clean_paths = {'.eggs',
                             'build',
                             PROJECT_NAME + '.egg-info',
                             'dist',
                             }
        self._clean_paths = {project_path.joinpath(p)
                             for p in self._clean_paths}
        self._clean_paths = {d for d in self._clean_paths if d.exists()}

    def initialize_options(self):
        """Unused, but required when implementing :class:`Command`."""
        pass

    def finalize_options(self):
        """Unused, but required when implementing :class:`Command`."""
        pass

    def run(self):
        """Performs the actual removal of the intermediate build directories."""
        for d in self._clean_paths:
            print(f'Removing {d}')
            rmtree(d)


setup(name=PROJECT_NAME,
      version=PROJECT_VERSION,
      author='Mike Durso',
      author_email='rbprogrammer@gmail.com',
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: MacOS',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Version Control :: Git',
          'Topic :: Utilities',
      ],
      cmdclass={'clean': CleanCommand},
      description='Another dotfiles manager.',
      include_package_data=True,
      install_requires=load_requirements('requirements.txt'),
      long_description=read_file(get_repo_file('README.md')),
      long_description_content_type='text/markdown',
      packages=get_dfmpy_packages(),
      package_data={'resources': ['*']},
      scripts=('bin/dfmpy',),
      tests_require=load_requirements('requirements.txt'),
      url='https://gitlab.com/rbprogrammer/dfmpy',
      )
