#!/usr/bin/env python
# -*- coding: utf-8 -*-

import templatepypipackage
import os.path as osp
from time import strftime
import os, logging, shutil
logger = logging.getLogger('templatepypipackagelogger')

class Setupper(object):
    """
    Sets up a new package directory structure based on the supplied
    package name.

    :param packname: Name of the package for which a new directory should be created.
    :type packname: str
    :param dry: Don't actually create the directory, only log
    :type dry: bool, optional
    :param workdir: Directory in which the package should be created. Defaults to `os.getcwd()`.
    :type workdir: str, optional
    """
    def __init__(self, packname, dry=False, workdir=None):
        """
        Constructor method
        """
        super(Setupper, self).__init__()
        self.packname = packname
        self.dry = dry
        self.workdir = os.getcwd() if (workdir is None) else workdir
        self.do_logger = True
        self.do_utils = True
        self.input_dir = osp.abspath(osp.join(osp.dirname(templatepypipackage.__file__), 'input'))

    def setup(self):
        """
        Runs the full chain of methods to setup a package directory
        """
        self.setup_directory_structure()
        with templatepypipackage.utils.switchdir(self.packname):
            self.setup_python_files()
            self.setup_package_files()
            self.setup_gitignore()

    def setup_directory_structure(self):
        """
        Creates all the necessary directories for the package
        """
        with templatepypipackage.utils.switchdir(self.workdir):
            templatepypipackage.utils.create_directory(self.packname, must_not_exist=True)
            templatepypipackage.utils.create_directory(osp.join(self.packname, 'bin'))
            templatepypipackage.utils.create_directory(osp.join(self.packname, self.packname))

    def setup_python_files(self):
        """
        Creates a minimal python package with an __init__.py, an Example class, and a logger/utils file
        """
        with templatepypipackage.utils.switchdir(self.packname):
            InitPythonFile(self.do_logger, self.do_utils).to_file('__init__.py')
            ExamplePythonFile(self.packname).to_file('example.py')
            if self.do_logger: LoggerPythonFile(self.packname).to_file('logger.py')
            if self.do_utils: UtilsPythonFile(self.packname).to_file('utils.py')

    def setup_package_files(self):
        """
        Creates a bunch of standard package files
        """
        setup = File()
        setup.contents.extend([
            "from setuptools import setup",
            "",
            "setup(",
            "    name          = '{0}',".format(self.packname),
            "    version       = '0.1',",
            "    license       = 'BSD 3-Clause License',",
            "    description   = 'Description text',",
            "    url           = 'https://github.com/tklijnsma/{0}.git',".format(self.packname),
            "    download_url  = 'https://github.com/tklijnsma/{0}/archive/v0_1.tar.gz',".format(self.packname),
            "    author        = 'Thomas Klijnsma',",
            "    author_email  = 'tklijnsm@gmail.com',",
            "    packages      = ['{0}'],".format(self.packname),
            "    zip_safe      = False,",
            "    tests_require = ['nose'],",
            "    test_suite    = 'nose.collector',",
            "    scripts       = [",
            "        'bin/{0}-run'".format(self.packname),
            "        ],",
            "    )",
            "",
            ])
        setup.to_file('setup.py')

        readme = File()
        readme.contents.extend([
            '# {0}'.format(self.packname),
            '',
            'Read me for package {0}'.format(self.packname),
            '',
            '## Heading 2',
            '',
            '```',
            'Some code',
            'On multiple lines',
            '```',
            '',
            ])
        readme.to_file('README.md')

        binfile = PythonFile()
        binfile.contents.extend([
            "import {0}".format(self.packname),
            "import argparse",
            "parser = argparse.ArgumentParser()",
            "parser.add_argument('argument', type=str, help='Some argument needed to run')",
            "# parser.add_argument( '--boolean', action='store_true', help='boolean')",
            "# parser.add_argument( '--list', metavar='N', type=str, nargs='+', help='list of strings' )",
            "args = parser.parse_args()",
            "",
            "def main():",
            "    example = {0}.Example()".format(self.packname),
            "    # example.run()",
            "",
            "if __name__ == '__main__':",
            "    main()",
            ])
        binfile.to_file('bin/{0}-run'.format(self.packname))


        license = File()
        license.contents.extend([
            'BSD 3-Clause License',
            '',
            'Copyright (c) {0}, Thomas Klijnsma'.format(strftime('%Y')),
            'All rights reserved.',
            '',
            'Redistribution and use in source and binary forms, with or without',
            'modification, are permitted provided that the following conditions are met:',
            '',
            '* Redistributions of source code must retain the above copyright notice, this',
            '  list of conditions and the following disclaimer.',
            '',
            '* Redistributions in binary form must reproduce the above copyright notice,',
            '  this list of conditions and the following disclaimer in the documentation',
            '  and/or other materials provided with the distribution.',
            '',
            '* Neither the name of the copyright holder nor the names of its',
            '  contributors may be used to endorse or promote products derived from',
            '  this software without specific prior written permission.',
            '',
            'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"',
            'AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE',
            'IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE',
            'DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE',
            'FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL',
            'DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR',
            'SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER',
            'CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,',
            'OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE',
            'OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.',
            ])
        license.to_file('LICENSE.txt')

    def setup_gitignore(self):
        """
        Copies a standard .gitignore file for python packages to the package dir
        """
        src = osp.join(self.input_dir, 'gitignore.txt')
        dst = '.gitignore'
        logger.info('Copying {0} ==> {1}'.format(src, dst))
        shutil.copyfile(src, dst)


class File(object):
    """
    Base class to write a file.
    """
    def __init__(self):
        super(File, self).__init__()
        self.contents = []

    def aggregate_contents(self):
        """
        Aggregates the contents.
        """
        return '\n'.join(self.contents)

    def to_file(self, filename):
        """
        Aggregates the contents and writes it to a file

        :param filename: File to be written to
        :type filename: str
        """
        logger.info('Opening {0} and dumping contents'.format(filename))
        with open(filename, 'w') as f:
            f.write(self.aggregate_contents())

class PythonFile(File):
    """
    Base class to write a .py file.
    """
    def __init__(self):
        super(PythonFile, self).__init__()
        self.contents.extend([
            '#!/usr/bin/env python',
            '# -*- coding: utf-8 -*-',
            ])

class InitPythonFile(PythonFile):
    """
    Writes the standard package __init__.py file

    :param do_logger: Adds lines to instantiate a Logger object
    :type do_logger: bool
    :param do_utils: Adds lines to import the utils file
    :type do_utils: bool
    """
    def __init__(self, do_logger, do_utils):
        """
        Constructor method
        """
        super(InitPythonFile, self).__init__()
        if do_logger:
            self.contents.extend([
                'from .logger import setup_logger',
                'logger = setup_logger()',
                '',
                ])
        if do_utils:
            self.contents.extend([
                'from . import utils',
                '',
                ])
        self.contents.extend([
            'from .example import Example',
            ])
        
class LoggerPythonFile(PythonFile):
    """
    Writes the logger.py file.

    :param packname: Name of the package
    :type package: str
    """
    def __init__(self, packname):
        """
        Constructor method
        """
        super(LoggerPythonFile, self).__init__()
        self.packname = packname
        self.contents.extend([
            'import logging',
            '',
            'DEFAULT_LOGGER_FORMATTER = logging.Formatter(',
            '    fmt = \'[{0}|%(levelname)8s|%(asctime)s|%(module)s]: %(message)s\','.format(self.packname),
            '    datefmt=\'%Y-%m-%d %H:%M:%S\'',
            '    )',
            '',
            'DEFAULT_LOGGER_NAME = \'{0}\''.format(self.packname),
            '',
            '',
            'def setup_logger(name=DEFAULT_LOGGER_NAME, formatter=DEFAULT_LOGGER_FORMATTER):',
            '    """',
            '    Creates a logger',
            '',
            '    :param name: Name of the logger',
            '    :type name: str, optional',
            '    :param formatter: logging.Formatter object which determines the log string format',
            '    :type formatter: logging.Formatter',
            '    """',
            '',
            '    handler = logging.StreamHandler()',
            '    handler.setFormatter(formatter)',
            '',
            '    logger = logging.getLogger(name)',
            '    logger.setLevel(logging.DEBUG)',
            '    logger.addHandler(handler)',
            '    return logger',
            ])

class UtilsPythonFile(PythonFile):
    """
    Writes the utils.py file.

    :param packname: Name of the package
    :type package: str
    """
    def __init__(self, packname):
        """
        Constructor method
        """
        super(UtilsPythonFile, self).__init__()
        self.packname = packname
        self.contents.extend([
            'import os, shutil, logging',
            'import os.path as osp',
            'import {0}'.format(self.packname),
            'logger = logging.getLogger(\'{0}\')'.format(self.packname), # will instantiate if no logger exists
            '',
            'def _create_directory_no_checks(dirname, dry=False):',
            '    """',
            '    Creates a directory without doing any further checks.',
            '',
            '    :param dirname: Name of the directory to be created',
            '    :type dirname: str',
            '    :param dry: Don\'t actually create the directory, only log',
            '    :type dry: bool, optional',
            '    """',
            '    logger.warning(\'Creating directory {0}\'.format(dirname))',
            '    if not dry: os.makedirs(dirname)',
            '',
            'def create_directory(dirname, force=False, must_not_exist=False, dry=False):',
            '    """',
            '    Creates a directory if certain conditions are met.',
            '',
            '    :param dirname: Name of the directory to be created',
            '    :type dirname: str',
            '    :param force: Removes the directory `dirname` if it already exists',
            '    :type force: bool, optional',
            '    :param must_not_exist: Throw an OSError if the directory already exists',
            '    :type must_not_exist: bool, optional',
            '    :param dry: Don\'t actually create the directory, only log',
            '    :type dry: bool, optional',
            '    """',
            '    if osp.isfile(dirname):',
            '        raise OSError(\'{0} is a file\'.format(dirname))',
            '    isdir = osp.isdir(dirname)',
            '',
            '    if isdir:',
            '        if must_not_exist:',
            '            raise OSError(\'{0} must not exist but exists\'.format(dirname))',
            '        elif force:',
            '            logger.warning(\'Deleting directory {0}\'.format(dirname))',
            '            if not dry: shutil.rmtree(dirname)',
            '        else:',
            '            logger.warning(\'{0} already exists, not recreating\')',
            '            return',
            '    _create_directory_no_checks(dirname, dry=dry)',
            '',
            'class switchdir(object):',
            '    """',
            '    Context manager to temporarily change the working directory.',
            '',
            '    :param newdir: Directory to change into',
            '    :type newdir: str',
            '    :param dry: Don\'t actually change directory if set to True',
            '    :type dry: bool, optional',
            '    """',
            '    def __init__(self, newdir, dry=False):',
            '        super(switchdir, self).__init__()',
            '        self.newdir = newdir',
            '        self._backdir = os.getcwd()',
            '        self._no_need_to_change = (self.newdir == self._backdir)',
            '        self.dry = dry',
            '',
            '    def __enter__(self):',
            '        if self._no_need_to_change:',
            '            logger.info(\'Already in right directory, no need to change\')',
            '            return',
            '        logger.info(\'chdir to {0}\'.format(self.newdir))',
            '        if not self.dry: os.chdir(self.newdir)',
            '',
            '    def __exit__(self, type, value, traceback):',
            '        if self._no_need_to_change:',
            '            return',
            '        logger.info(\'chdir back to {0}\'.format(self._backdir))',
            '        if not self.dry: os.chdir(self._backdir)',
            ])

class ExamplePythonFile(PythonFile):
    """
    Writes the example.py file

    :param packname: Name of the package
    :type package: str
    """
    def __init__(self, packname):
        """
        Constructor method
        """
        super(ExamplePythonFile, self).__init__()
        self.packname = packname
        self.contents.extend([
            'import {0}'.format(self.packname),
            'import os.path as osp',
            'import logging',
            'logger = logging.getLogger(\'{0}\')'.format(self.packname),
            '',
            'class Example(object):',
            '    """',
            '    Example docstring',
            '',
            '    :param variable: Description of some variable',
            '    :type variable: str, optional',
            '    """',
            '    def __init__(self, variable=\'\'):',
            '        """',
            '        Constructor method',
            '        """',
            '        super(Example, self).__init__()',
            '        self.variable = variable',
            ])

