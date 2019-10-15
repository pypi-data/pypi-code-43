#!/usr/bin/env python
#
# main.py - The FSL Evaluation and Example Data Suite, now in Python!
#
# Authors: Matthew Webster and Paul McCarthy, FMRIB.
#
"""The FSL Evaluation and Example Data Suite (FEEDS), now in Python!

Pyfeeds (the FMRIB Evaluation and Example Data Suite) is a framework for
running and managing tests for the FSL code base.


See the following documents  for details on pyfeeds:

  - Using pyfeeds:                  ``doc/using_pyfeeds.md``
  - How to write a pyfeeds test:    ``doc/writing_a_test.md``
  - How pyfeeds works:              ``doc/how_pyfeeds_works.md``
  - The pyfeeds configuration file: ``doc/configuring_pyfeeds.md``


-----------------
Pyfeeds internals
-----------------


The pyfeeds logic is split across a few separate modules:

 - This module contains the :class:`Pyfeeds` class, the :func:`main` function
   (the pyfeeds entry point), and argument parsing logic.

 - The :mod:`.testing` module contains the :class:`.Test` class, and
   functions for identifying and running tests.

 - The :mod:`.evaluate` module contains functions for evaluating test results.

 - The :mod:`.hashing` module contains functions for test verification (to
   identify when tests or test data have changed).

 - The :mod:`.common` module contains other miscellaneous functions.


The :func:`main` function is the entry point for pyfeeds. It parses arguments
and a configuration file (if one was specified), and creates a
:class:`Pyfeeds` object. This object combines the command line and
configuration file settings, identifies all of the tests in the provided test
directories, and creates a :class:`.Test` object for each of them. The
:func:`main` function then calls one of the following functions, depending
upon which sub-command the user has specified:


  ============= =============================
  *Command*     *Function*
  ``list``      :func:`.testing.listTests`
  ``run``       :func:`.testing.runTests`
  ``bundle``    :func:`.testing.bundleTests`
  ``genhash``   :func:`.hashing.genHashes`
  ``checkhash`` :func:`.hashing.checkHashes`
  ``compare``   :func:`.evaluate.compareDirs`
  ============= =============================
"""


from __future__ import print_function
from __future__ import division

import os.path as op
import            os
import            sys
import            logging
import            fnmatch
import            argparse
import            datetime
import            functools
import            configparser
from collections import OrderedDict

from . import __version__ as pyfeeds_version
from . import common
from . import testing
from . import hashing
from . import evaluate
from . import imagecache


log = logging.getLogger()


ARG_SEP = ':'
"""String used as a separator character in the `--selfEval`, `--evalRoutines`,
`--exclude`, `--tolerances`, and `--fileGroups` command-line arguments.
"""


class Pyfeeds(object):
    """The ``Pyfeeds`` class is used as a container for:

        - command line arguments
        - settings read from the pyfeeds configuration file
        - the list of tests to be considered


    A ``Pyfeeds`` instance is created in the :func:`main` function, and passed
    around the various parts of ``pyfeeds``. Only one ``Pyfeeds`` instance
    should ever exist.
    """


    def __init__(self, args, cfg):
        """Create the ``Pyfeeds`` instance.

        Combines the command line and configuration file arguments, and
        creates a :class:`.Test` instance for all identified tests.

        :arg args: ``argparse.Namespace`` object containing parsed command
                   line arguments. It is assumed that, if an argument was
                   not passed in on the command line, it is set to ``None``.

        :arg cfg: ``argparse.Namespace`` object containing settings loaded
                   from a pyfeeds configuration file.  It is assumed that, if
                   an argument was not present in the configuration file, it
                   is present in this object.
        """

        # Default values for all settings
        self.verbose          = False
        self.quiet            = False
        self.includeTests     = None
        self.excludeTests     = None
        self.testDir          = []
        self.inputDir         = None
        self.benchmarkDir     = None
        self.outputDir        = None
        self.overwrite        = False
        self.outputFile       = None
        self.config           = None
        self.hashFile         = None
        self.jobs             = 1
        self.updateHashes     = False
        self.skipHashes       = False
        self.forceHashes      = False
        self.sandboxDir       = None
        self.leaveSandboxes   = False
        self.selfEval         = []
        self.evalRoutines     = {'*' : ['evalMD5']}
        self.fileGroups       = []
        self.exclude          = []
        self.tolerances       = {}
        self.defaultTolerance = 0.05
        self.genHashes        = False
        self.cacheSize        = 32768
        self.imageCache       = None

        for key, val in cfg.__dict__.items():

            log.debug('Applying config file setting:  {} = {}'.format(key,
                                                                      val))
            setattr(self, key, val)

        for key, val in args.__dict__.items():
            if val is None:
                continue

            log.debug('Applying command line setting: {} = {}'.format(key,
                                                                      val))

            setattr(self, key, val)

        # Hashfile defaults to inputDir/.feedsHashes,
        # but we record whether the user actually
        # specified a hash file - if they don't
        # explicitly specify a hashfile, the genhash
        # command will print to stdout.
        self.hashFileProvided = self.hashFile is not None

        if self.hashFile is None and self.inputDir is not None:
            hashFile = op.join(self.inputDir, '.feedsHashes')
            if op.exists(hashFile):
                self.hashFile = hashFile

        # Figure out when the hash file was last generated
        if self.hashFile is not None and op.exists(self.hashFile):
            mtime = op.getmtime(self.hashFile)
            mtime = datetime.datetime.fromtimestamp(mtime)
            self.hashesLastGenerated = mtime
        else:
            self.hashesLastGenerated = None

        # Add a "*/" at the beginning of every file
        # name pattern, because the evaluate module
        # tests absolute file paths.
        def absify(p):
            return '*{}{}'.format(op.sep, p)

        self.exclude      = [absify(e) for e in self.exclude]
        self.evalRoutines = {absify(k) : v
                             for k, v in self.evalRoutines.items()}
        self.tolerances   = {absify(k) : v
                             for k, v in self.tolerances.items()}

        # All files in a group are currently
        # assumed to be in the same directory
        self.fileGroups = [[op.basename(p) for p in g]
                           for g in self.fileGroups]

        self.tests = self.__findTests(self.testDir)
        self.__validate()

        self.imageCache = imagecache.ImageCache(maxsize=self.cacheSize)


    def __findTests(self, testDirs):
        """Finds all pyfeeds tests in the given set of directories.

        :returns: A list of :class:`.Test` instances.
        """

        # Find all test sub-directories contained within
        # the directories specified by the user
        testDirs = [testing.findTestDirs(d) for d in testDirs]

        if len(testDirs) == 0:
            return []

        testDirs = functools.reduce(lambda a, b: a + b, testDirs)
        testDirs = sorted(set(testDirs))

        if len(testDirs) == 0:
            return []

        # remove any tests that don't
        # match the include patterns
        if self.includeTests is not None:
            filtered = []
            for td in testDirs:
                if any([fnmatch.fnmatch(td, p) for p in self.includeTests]):
                    filtered.append(td)
            testDirs = filtered

        # Remove any tests which match
        # the exclude patterns
        if self.excludeTests is not None:
            filtered = []
            for td in testDirs:
                if not any([fnmatch.fnmatch(td, p)
                            for p in self.excludeTests]):
                    filtered.append(td)
            testDirs = filtered

        # Find the deepest directory in
        # the file system which contains
        # all of the detected tests.
        rootDir = common.findCommonAncestor(testDirs)
        log.debug('Root of all test directories: {}'.format(rootDir))

        # Create a Test object for each
        # one of the test directories
        tests = []
        for td in testDirs:
            for script in testing.findTestScripts(td):
                try:
                    tests.append(testing.Test(script, rootDir))
                except Exception as e:
                    log.warning('Error loading test {} ({})'.format(td, e))

        return tests


    def __validate(self):
        """Performs some simple validation to make sure that the user
        has specified all required arguments.
        """

        notests      = 'No tests specified!'
        noinput      = 'Input data directory not specified or invalid!'
        nooutputdir  = 'Output directory not specified!'
        outputexist  = 'Output directory already exists!'
        nobenchmark  = 'Benchmark data directory not specified or invalid!'
        badroutine   = '{} is not a valid evaluation routine!'

        command      = self.command
        tests        = self.tests
        inputDir     = self.inputDir
        benchmarkDir = self.benchmarkDir
        outputDir    = self.outputDir
        ovw          = self.overwrite

        # all commands except for
        # compare need some tests
        if command != 'compare' and len(tests) == 0:
            raise RuntimeError(notests)

        if command in ('run', 'bundle'):

            if outputDir is None:
                raise RuntimeError(nooutputdir)
            if op.exists(outputDir) and not ovw:
                raise RuntimeError(outputexist)
            if (inputDir is not None) and (not op.exists(inputDir)):
                raise RuntimeError(noinput)
            if (benchmarkDir is not None) and (not op.exists(benchmarkDir)):
                raise RuntimeError(nobenchmark)

        elif command == 'compare':

            if inputDir     is None:        raise RuntimeError(noinput)
            if benchmarkDir is None:        raise RuntimeError(nobenchmark)
            if not op.exists(inputDir):     raise RuntimeError(noinput)
            if not op.exists(benchmarkDir): raise RuntimeError(nobenchmark)

        elif command in ('genhash', 'checkhash'):
            if (inputDir is not None) and (not op.exists(inputDir)):
                raise RuntimeError(noinput)

        for testName, routines in self.evalRoutines.items():
            for routine in routines:
                if not hasattr(evaluate, routine):
                    raise RuntimeError(badroutine.format(routine))


def main(argv=None):
    """Pyfeeds entry point. This function does the following:

      1. Parses command line arguments (via the :func:`parseArgs` function).

      2. Loads a configuration file if one was specified (via the
         :func:`loadPyfeedsConfig` function).

      3. Creates a :class:`Pyfeeds` object.

      4. Calls the command function which corresponds to the sub-command
         that was specified by the user:

         .. autosummary::
            :nosignatures:

            .testing.listTests
            .testing.runTests
            .testing.bundleTests
            .hashing.genHashes
            .hashing.checkHashes
            .evaluate.compareDirs

    :arg argv: Command line arguments. If not provided, ``sys.argv`` is used.
    """

    args = parseArgs(argv)
    cfg  = loadPyfeedsConfig(args.config)

    configLogging(args, cfg)

    pyfeeds = Pyfeeds(args, cfg)

    log.info('pyfeeds %s', pyfeeds_version)

    # Do that thing we were asked to do
    if   args.command == 'list':      testing .listTests(  pyfeeds)
    elif args.command == 'run':       testing .runTests(   pyfeeds)
    elif args.command == 'bundle':    testing .bundleTests(pyfeeds)
    elif args.command == 'genhash':   hashing .genHashes(  pyfeeds)
    elif args.command == 'checkhash': hashing .checkHashes(pyfeeds)
    elif args.command == 'compare':   evaluate.compareDirs(pyfeeds)


def configLogging(args, cfg):
    """Configures logging, including verbosity, and streaming to a file.
    """
    def getarg(name):

        argval = getattr(args, name, None)
        cfgval = getattr(cfg,  name, None)

        if argval: return argval
        else:      return cfgval

    verbose = getarg('verbose')
    quiet   = getarg('quiet')
    logFile = getarg('logFile')

    logger = logging.getLogger()
    fmt    = logging.Formatter('%(levelname)8.8s '
                               '%(filename)20.20s '
                               '%(lineno)4d: '
                               '%(funcName)-15.15s - '
                               '%(message)s')

    if logFile is None: handler = logging.StreamHandler()
    else:               handler = logging.FileHandler(logFile)

    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if   verbose: logger.setLevel(logging.DEBUG)
    elif quiet:   logger.setLevel(logging.CRITICAL + 1)
    else:         logger.setLevel(logging.INFO)


def parseArgs(argv):
    """Parses command line arguments.

    :arg argv:  List of arguments - if None, sys.argv is used.

    :returns:   An ``argparse.Namespace`` object.
    """

    if argv is None:
        argv = sys.argv[1:]

    # If the user gave us nothing,
    # give them some help
    if len(argv) == 0:
        argv = ['--help']

    usages = {
        'mainParser' :
        'pyfeeds command            [options] [testDir ...]\n'
        'pyfeeds command -c cfgfile [options] [testDir ...]\n',

        'list' :
        'pyfeeds list [testDir ...]',

        'run' :
        'pyfeeds run\n'
        '          -i inputDir\n'
        '          -b benchmarkDIr\n'
        '          -o outputDir\n'
        '          [options] [testDir ...]',

        'bundle' :
        'pyfeeds bundle\n'
        '          -i inputDir\n'
        '          -b benchmarkDir\n'
        '          -o outputDir\n'
        '          [options] [testDir ...]',

        'genhash' :
        'pyfeeds genhash -i inputDir [options] [testDir ...]',

        'checkhash' :
        'pyfeeds checkhash -i inputDir [options] [testDir ...]',

        'compare' :
        'pyfeeds compare [options] inputDir benchmarkDir\n',
    }

    flags = {

        # global options
        'version'        : ('-V',  '--version'),
        'verbose'        : ('-v',  '--verbose'),
        'quiet'          : ('-q',  '--quiet'),
        'logFile'        : ('-lf', '--logFile'),
        'includeTests'   : ('-it', '--includeTests'),
        'excludeTests'   : ('-et', '--excludeTests'),
        'cacheSize'      : ('-cs', '--cacheSize'),
        'testDir'        : 'testDir',

        # shared options
        'inputDir'       : ('-i',  '--inputDir'),
        'benchmarkDir'   : ('-b',  '--benchmarkDir'),
        'outputDir'      : ('-o',  '--outputDir'),
        'overwrite'      : ('-w',  '--overwrite'),
        'config'         : ('-c',  '--config'),
        'hashFile'       : ('-a',  '--hashFile'),
        'forceHashes'    : ('-fh', '--forceHashes'),

        # run options
        'jobs'             : ('-j', '--jobs'),
        'updateHashes'     : ('-u', '--updateHashes'),
        'skipHashes'       : ('-k', '--skipHashes'),
        'sandboxDir'       : ('-n', '--sandboxDir'),
        'leaveSandboxes'   : ('-l', '--leaveSandboxes'),
        'selfEval'         : ('-s', '--selfEval'),
        'evalRoutines'     : ('-e', '--evalRoutines'),
        'exclude'          : ('-x', '--exclude'),
        'tolerances'       : ('-t', '--tolerances'),
        'defaultTolerance' : ('-d', '--defaultTolerance'),
        'fileGroups'       : ('-f', '--fileGroups'),

        # bundle options
        'genHashes'        : ('-g',  '--genHashes'),

        # compare options
        'outputFile'       : ('-o', '--outputFile'),
    }

    helps = {
        # Commands
        'list'             : 'List available tests',
        'run'              : 'Run tests',
        'bundle'           : 'Bundle tests',
        'genhash'          : 'Generate test hashes',
        'checkhash'        : 'Validate test hashes',
        'compare'          : 'Compare two directories',

        # Global options
        'verbose'          : 'Print additional debug messages',
        'quiet'            : 'Suppress all unrequested '
                             'output (including warnings)',
        'logFile'          : 'Write log messages to this file (default: '
                             'log messages are written to standard output).',
        'testDir'          : 'Directory containing tests (default: current '
                             'directory)',
        'includeTests'     : 'Only consider tests matching this wildcard '
                             'pattern. Can be used multiple times. ',
        'excludeTests'     : 'Do not consider tests matching this wildcard '
                             'pattern. Takes precedence over --includeTests. '
                             'Can be used multiple times. ',
        'cacheSize'        : 'Size (MB) to use for the internal image cache '
                             '(default: 32768)',

        # Shared options
        'inputDir'         : 'Location of input data directory',
        'benchmarkDir'     : 'Location of benchmark data directory',
        'outputDir'        : 'Location of output directory',
        'overwrite'        : 'Overwrite output directory if it exists',
        'config'           : 'Pyfeeds configuration file',
        'hashFile'         : 'File to read/write test hashes (default: '
                             '[inputDir]/.feedsHashes',
        'forceHashes'      : 'Force test hashing, even if file modification '
                             'times suggest that the data has not been '
                             'modified since the last check.',

        # Run options
        'jobs'             : 'Number of jobs to run in parallel',

        'updateHashes'     : 'Update test data hashes',
        'skipHashes'       : 'Skip test hash verification',
        'sandboxDir'       : 'Directory to store test sandboxes '
                             '(default: temporary location)',
        'leaveSandboxes'   : 'Do not delete test sandbox directories',
        'selfEval'         : 'List of tests which evaluate themselves. '
                             'Specify the list as a single argument (quoted '
                             'if necessary), with tests separated by the '
                             '{} character.'.format(ARG_SEP),
        'evalRoutines'     : 'List of (file pattern, [evaluation routine]) '
                             'pairs. Specify the list as a single argument '
                             '(quoted if necessary), with pairs separated '
                             'by the {} character, and with each pair '
                             'having the form '
                             '"pattern=routine1,routine2,...".'.format(
                                 ARG_SEP),
        'exclude'          : 'List of file patterns, separated with the {} '
                             'character (and quoted if necessary), '
                             'specifying files which should not be '
                             'evaluated. This list takes precedence over the '
                             'file patterns specified via the "{}" '
                             'argument.'.format(
                                 ARG_SEP, flags['evalRoutines'][1]),
        'tolerances'       : 'List of (file pattern, tolerance) pairs.'
                             'Specify the list as a single argument '
                             '(quoted if necessary), with pairs separated '
                             'by the {} character, and with each pair '
                             'having the form '
                             '"pattern=tolerance".'.format(ARG_SEP),
        'defaultTolerance' : 'Default tolerance to use for files which '
                             'do not have a specific tolerance specified '
                             'via the "{}" argument. '.format(
                                 flags['tolerances'][1]),
        'fileGroups'       : 'List of file patterns denoting groups of '
                             'files which should be evaluated together. '
                             'Specify all groups as a single argument, '
                             'where groups are separated by the {} '
                             'character, and with each group having the '
                             'form "pattern1,pattern2,pattern3,'
                             '...". All files in a group are assumed to '
                             'be in the same directory.'.format(ARG_SEP),

        # Bundle options
        'genHashes'        : 'Generate hashes for bundled tests. The '
                             'hashes are saved in '
                             '[outputDir]/[inputDir]/.feedsHashes',

        # Compare options
        'outputFile'       : 'Save results to this file (default: print to '
                             'standard output).',
    }

    descs = {
        'mainParser' :
        'Pyfeeds allows you to run and manage the FSL test suite. Choose\n'
        'one of the pyfeeds commands, and specify a set of directories\n'
        'which contain tests.',

        'list' :
        'The \'list\' command lists all of the tests that are found in\n'
        'the specified test directories.',

        'run' :
        'The \'run\' command runs and evaluates all detected tests, and\n'
        'prints a summary of passes and failures.',

        'bundle' :
        'The \'bundle\' command copies all detected tests and their\n'
        'associated data into a new stand-alone directory.',

        'genhash' :
        'The \'genhash\' command calculates hashes of all detected tests\n'
        'and test data, for verification purposes.',

        'checkhash' :
        'The \'checkhash\' command calculates hashes of all detected\n'
        'tests and test data, compares them to the stored test hashes,\n'
        'and prints a summary of which tests have changed.',

        'compare' :
        'The \'compare\' command compares two directories to each other,\n'
        'and outputs a summary of the difference between them.',
    }

    epilogs = {
        'mainParser' :
        'To get help on a pyfeeds command, type\n\n'
        '    pyfeeds command --help',

        'list'    : None,
        'bundle'  : None,
        'compare' :
        'Available evaluation routines are:\n{}'.format(
            '\n'.join(['  {}'.format(r) for r in evaluate.listRoutines()])),

        'run' :
        'If the hashFile argument is not provided, the test hashes are \n'
        'assumed to be located at:\n\n'
        '    [inputDir]/.feedsHashes\n\n'
        'Available evaluation routines are:\n{}'.format(
            '\n'.join(['  {}'.format(r) for r in evaluate.listRoutines()])),

        'genhash' :
        'If the hashFile argument is not provided, the test hashes are\n'
        'printed to standard output.',

        'checkhash' :
        'If the hashFile argument is not provided, the test hashes are\n'
        'assumed to be located at:\n\n'
        '    [inputDir]/.feedsHashes',
    }

    mainParser = argparse.ArgumentParser(
        prog='pyfeeds',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=descs['mainParser'],
        usage=usages['mainParser'],
        epilog=epilogs['mainParser'])

    # Global options shared by all sub-commands
    baseParser = argparse.ArgumentParser(add_help=False)
    baseParser.add_argument(*flags['version'],
                            action='version',
                            version=pyfeeds_version)
    baseParser.add_argument(*flags['config'],
                            help=helps['config'])
    baseParser.add_argument(*flags['logFile'],
                            help=helps['logFile'])
    baseParser.add_argument(*flags['includeTests'],
                            help=helps['includeTests'],
                            action='append')
    baseParser.add_argument(*flags['excludeTests'],
                            help=helps['excludeTests'],
                            action='append')
    baseParser.add_argument(*flags['cacheSize'],
                            help=helps['cacheSize'],
                            type=int)

    vqParser = baseParser.add_mutually_exclusive_group()
    vqParser.add_argument(*flags['verbose'],
                          help=helps['verbose'],
                          action='store_true')
    vqParser.add_argument(*flags['quiet'],
                          help=helps['quiet'],
                          action='store_true')

    # Options shared by all sub-commands except 'compare'
    testBaseParser = argparse.ArgumentParser(add_help=False)
    testBaseParser.add_argument(flags['testDir'],
                                help=helps['testDir'],
                                nargs='*')

    # Options shared by the run/bundle/genhash/checkhash sub-commands
    runbungencheckParser = argparse.ArgumentParser(add_help=False)
    runbungencheckParser.add_argument(*flags['inputDir'],
                                      help=helps['inputDir'])

    # Options shared by the run/bundle sub-commands
    runbunParser = argparse.ArgumentParser(add_help=False)
    runbunParser.add_argument(*flags['outputDir'],
                              help=helps['outputDir'])
    runbunParser.add_argument(*flags['overwrite'],
                              help=helps['overwrite'],
                              action='store_true')
    runbunParser.add_argument(*flags['benchmarkDir'],
                              help=helps['benchmarkDir'])

    # Options shared by the run/genhash/checkhash sub-commands
    rungencheckParser = argparse.ArgumentParser(add_help=False)
    rungencheckParser.add_argument(*flags['hashFile'],
                                   help=helps['hashFile'])

    # Options shared by the run/checkhash sub-commands
    runcheckParser = argparse.ArgumentParser(add_help=False)
    runcheckParser.add_argument(*flags['forceHashes'],
                                action='store_true',
                                help=helps['forceHashes'])

    # Options for the compare sub-command
    compareParser = argparse.ArgumentParser(add_help=False)
    compareParser.add_argument('inputDir',
                               help=helps['inputDir'])
    compareParser.add_argument('benchmarkDir',
                               help=helps['benchmarkDir'])
    compareParser.add_argument(*flags['outputFile'],
                               help=helps['outputFile'])

    # Options shared by the run/compare sub-commands
    runcmpParser = argparse.ArgumentParser(add_help=False)
    runcmpParser.add_argument(*flags['selfEval'],
                              help=helps['selfEval'])
    runcmpParser.add_argument(*flags['evalRoutines'],
                              help=helps['evalRoutines'])
    runcmpParser.add_argument(*flags['exclude'],
                              help=helps['exclude'])
    runcmpParser.add_argument(*flags['tolerances'],
                              help=helps['tolerances'])
    runcmpParser.add_argument(*flags['defaultTolerance'],
                              help=helps['defaultTolerance'],
                              type=float)
    runcmpParser.add_argument(*flags['fileGroups'],
                              help=helps['fileGroups'])

    parents = {
        'list'      : [baseParser, testBaseParser],
        'run'       : [baseParser, testBaseParser, runbungencheckParser,
                       runbunParser, rungencheckParser, runcheckParser,
                       runcmpParser],
        'bundle'    : [baseParser, testBaseParser, runbungencheckParser,
                       runbunParser],
        'genhash'   : [baseParser, testBaseParser, runbungencheckParser,
                       rungencheckParser],
        'checkhash' : [baseParser, testBaseParser, runbungencheckParser,
                       rungencheckParser, runcheckParser],
        'compare'   : [baseParser, compareParser, runcmpParser]
    }

    # parsers for each sub-command
    subParserObjs = {}
    subParsers    = mainParser.add_subparsers(title='Pyfeeds commands',
                                              dest='command')

    for cmd in ['list', 'run', 'bundle', 'genhash', 'checkhash', 'compare']:
        subParserObjs[cmd] = subParsers.add_parser(
            cmd,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=parents[cmd],
            usage=usages[cmd],
            help=helps[cmd],
            description=descs[cmd],
            epilog=epilogs[cmd])

    # run options
    runParser = subParserObjs['run']
    runParser.add_argument(*flags['sandboxDir'],
                           help=helps['sandboxDir'])
    runParser.add_argument(*flags['jobs'],
                           help=helps['jobs'],
                           type=int)
    runParser.add_argument(*flags['skipHashes'],
                           help=helps['skipHashes'],
                           action='store_const',
                           const=True)
    runParser.add_argument(*flags['updateHashes'],
                           help=helps['updateHashes'],
                           action='store_const',
                           const=True)
    runParser.add_argument(*flags['leaveSandboxes'],
                           help=helps['leaveSandboxes'],
                           action='store_const',
                           const=True)

    # bundle options
    bundleParser = subParserObjs['bundle']
    bundleParser.add_argument(*flags['genHashes'],
                              help=helps['genHashes'],
                              action='store_const',
                              const=True)

    args = mainParser.parse_args(argv)

    # If no test dirs were passed,
    # set args.testDir to cwd
    if args.command != 'compare' and \
       (not hasattr(args, 'testDir') or len(args.testDir) == 0):
        args.testDir = [os.getcwd()]

    if args.command not in ('run', 'compare'):
        return args

    # The selfEval argument needs to be
    # turned from a string of the form:
    #
    #   test1:test2:test3
    #
    # into a list of test names
    if args.selfEval is not None:
        selfEval      = args.selfEval.split(ARG_SEP)
        selfEval      = [t.strip() for t in selfEval if t is not None]
        args.selfEval = selfEval

    # evalRoutines needs to be turned from
    # a string of the form:
    #
    #   pattern1=routine1:pattern2=routine1,routine2:testpattern3:routine1
    #
    # into a dictionary of
    #
    #   { testName : [routine] }
    #
    # mappings. The routines are kept as
    # strings for the time being - they
    # are validated by the Pyfeeds object.
    if args.evalRoutines is not None:
        evalRoutines = args.evalRoutines.split(ARG_SEP)
        evalRoutines = [r.split('=') for r in evalRoutines]

        for i, (pat, routines) in enumerate(evalRoutines):
            routines        = routines.split(',')
            routines        = [r.strip() for r in routines]
            evalRoutines[i] = (pat, routines)

        args.evalRoutines = OrderedDict(evalRoutines)

    # exclude needs to be turned from a
    # string of the form:
    #
    #   pattern1:pattern2:pattern3
    #
    # into a list of patterns.
    if args.exclude is not None:
        exclude      = args.exclude.split(ARG_SEP)
        exclude      = [p.strip() for p in exclude if p is not None]
        args.exclude = exclude

    # Tolerances needs to be turned from
    # a string of the form:
    #
    #   pattern1=tolerance:pattern2=tolerance:pattern3:tolerance
    #
    # into a dictionary of
    #
    #   { patern : tolerance }
    #
    # mappings.
    if args.tolerances is not None:
        tolerances      = args.tolerances.split(ARG_SEP)
        tolerances      = [t.split('=') for t in tolerances]
        tolerances      = [(n, float(t)) for (n, t) in tolerances]
        args.tolerances = OrderedDict(tolerances)

    # fileGroups needs to be turned from a
    # string of the form:
    #
    #   fg1pat1,fg1pat2:fg2pat1,fg2pat2,fg2pat3
    #
    # into a list of file pattern groups.
    if args.fileGroups is not None:
        fileGroups      = args.fileGroups.split(ARG_SEP)
        fileGroups      = [fg.split(',') for fg in fileGroups]
        fileGroups      = [[p.strip() for p in fg] for fg in fileGroups]
        args.fileGroups = fileGroups

    return args


def loadPyfeedsConfig(cfgfile):
    """Loads settings from the given pyfeeds configuration file.

    :arg cfgfile: Path to a pyfeeds configuration file.

    :returns:     An ``argparse.Namespace`` object containing all of the
                  settings that were present in the file
    """

    args = argparse.Namespace()

    if cfgfile is None:
        return args

    if not op.exists(cfgfile):
        raise RuntimeError('{} does not exist!'.format(cfgfile))

    def strbool(s):
        if s.lower() == 'false': return False
        else:                    return bool(s)

    def strlist(s):
        items = [i.strip() for i in s.split('\n')]
        items = [i for i in items if i != '']
        return items

    def strlistlist(s):
        items = [i.strip()                 for i in s.split('\n')]
        items = [i                         for i in items if i != '']
        items = [i.split(',')              for i in items]
        items = [[ii.strip()  for ii in i] for i in items]
        return items

    types = {
        'verbose'          : strbool,
        'quiet'            : strbool,
        'updateHashes'     : strbool,
        'skipHashes'       : strbool,
        'forceHashes'      : strbool,
        'leaveSandboxes'   : strbool,
        'genHashes'        : strbool,
        'defaultTolerance' : float,
        'jobs'             : int,
        'selfEval'         : strlist,
        'testDir'          : strlist,
        'exclude'          : strlist,
        'fileGroups'       : strlistlist,
        'includeTests'     : strlist,
        'excludeTests'     : strlist
    }

    # Use a case-sensitive file parser
    cfg             = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(cfgfile)

    generalSettings     = cfg.options('general')
    evalRoutinePatterns = cfg.options('evalRoutines')
    tolerancePatterns   = cfg.options('tolerances')

    evalRoutines = [cfg.get('evalRoutines', p)
                    for p in evalRoutinePatterns]

    evalRoutines = [r.split(',') for r in evalRoutines]
    evalRoutines = [[r.strip() for r in er] for er in evalRoutines]
    evalRoutines = reversed(list(zip(evalRoutinePatterns, evalRoutines)))
    evalRoutines = OrderedDict(evalRoutines)

    tolerances   = [cfg.getfloat('tolerances', p)
                    for p in tolerancePatterns]
    tolerances   = reversed(list(zip(tolerancePatterns,   tolerances)))
    tolerances   = OrderedDict(tolerances)

    if len(evalRoutines) > 0: args.evalRoutines = evalRoutines
    if len(tolerances)   > 0: args.tolerances   = tolerances

    for key in generalSettings:

        typecnv = types.get(key, str)
        val     = typecnv(cfg.get('general', key))

        setattr(args, key, val)

    return args


if __name__ == '__main__':
    """Calls the :func:`main` function. """
    main()
