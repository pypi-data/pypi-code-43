#!/usr/bin/env python
"""
Functions to convert python filenames into more simplified forms.

During the use of the backtrace functions it is commonly necessary
to print filenames. These filenames may be long and tedious  - when
all we care about is the trailing part of the name and where they
were included from.

We can reduce the names using the environment variables.
"""

import collections
import os
import site
import sys
import threading
import traceback


class ReduceFilename(object):
    """
    Convert the filename of a script to one that can be shown.

    Commonly the filenames are fully qualified and if we end up tracing
    into the standard library, we find that the names get very long.
    """
    _initialised = False
    _cached = None
    _cached_id = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            cache_id = cls.__cache_id()
            if cls._cached_id == cache_id:
                return cls._cached

            new_obj = super(ReduceFilename, cls).__new__(cls, *args, **kwargs)
            cls._cached = new_obj
            cls._cached_id = cache_id
            return new_obj

    @staticmethod
    def __cache_id():
        return set(sys.path)

    def __init__(self):
        """
        Construct the new information about simplifying the filenames.
        """
        with self._lock:
            if self._initialised:
                return

            self.paths = sys.path[:]
            pythonversion = '.'.join([str(x) for x in sys.version_info[0:2]])

            self.pathrules = []

            # Leave alone anything that looks like stdin/console
            def generate_path_stdin(_, path):
                if path[0] == '<' and path[-1] == '>':
                    return ['']
                return None

            self.pathrules.append({
                'prefix': '',
                'paths': generate_path_stdin,
            })

            self.venvbase = None
            self.sysbase = sys.prefix
            syspaths = [path for path in self.paths if path.startswith(self.sysbase)]

            # VirtualEnv overrides the system path
            if 'VIRTUAL_ENV' in os.environ:
                self.venvbase = os.path.abspath(os.environ['VIRTUAL_ENV'])
                self.venvbase_normalised = os.path.normcase(self.venvbase)
                pathlist = [path for path in self.paths if os.path.normcase(path).startswith(self.venvbase_normalised)]
                pathlist.append(self.venvbase)
                pathlist = sorted(pathlist, key=lambda x: -len(x))

                self.pathrules.append({
                    'prefix': '<venv>',
                    'paths': pathlist,
                })

                # To determine the system prefix, we need to dereference one of the symlinks
                # that is used within the venv.
                self.sysbase = None
                try:
                    prefix = None
                    ospath = os.__file__
                    if ospath.endswith('.pyc'):
                        ospath = ospath[:-1]

                        # The 'readlink' function does not exist on Windows
                        if hasattr(os, 'readlink') and hasattr(os.path, 'islink'):
                            if os.path.islink(ospath):  # pylint: disable=E1101
                                ospath = os.readlink(ospath)  # pylint: disable=E1101
                            if ospath.endswith('os.py'):
                                ospath = ospath[:-6]
                                lib = '/lib/python%s' % (pythonversion,)
                                if ospath.endswith(lib):
                                    prefix = ospath[:-len(lib)]

                    # On Windows there are no symlinks, so we instead read the 'orig-prefix.txt' file to
                    # find the system libraries.
                    if prefix is None:
                        origprefix = os.path.join(self.venvbase, 'Lib', 'orig-prefix.txt')
                        if os.path.isfile(origprefix):
                            with open(origprefix, 'r') as fh:
                                prefix = fh.read().strip()

                    # When executed within the virtualenv, sys.real_prefix will contain
                    # the system prefix as it was originally.
                    if hasattr(sys, 'real_prefix'):
                        prefix = os.path.normcase(sys.real_prefix)  # pylint: disable=E1101

                    if prefix is not None:
                        self.sysbase = prefix
                        syspaths = [self.sysbase + path[len(self.venvbase):]
                                    for path in self.paths
                                    if os.path.normcase(path).startswith(self.venvbase_normalised)]
                        syspaths = sorted(syspaths, key=lambda x: -len(x))

                except Exception as ex:  # pylint: disable=W0703
                    print("Exception whilst looking for VirtualEnv system path: %s" % (ex,))
                    lines = traceback.format_exc()
                    for line in lines:
                        print("    %s" % (line,))

            if self.sysbase:
                syspaths = sorted(syspaths, key=lambda x: -len(x))
                self.pathrules.append({
                    'prefix': '<syslib>',
                    'paths': syspaths,
                })

            if sys.platform == "darwin":
                # for framework builds *only* we add the standard Apple
                # locations.
                from sysconfig import get_config_var
                framework = get_config_var("PYTHONFRAMEWORK")
                if framework:
                    pathlist = [os.path.join("/Library", framework, sys.version[:3], "site-packages")]
                    self.pathrules.append({
                        'prefix': '<rootlib>',
                        'paths': pathlist,
                    })

            if site.ENABLE_USER_SITE:
                self.pathrules.append({
                    'prefix': '<userlib>',
                    'paths': [site.getusersitepackages()],  # pylint: disable=E1101
                })

            try:
                self.maindir = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))

                def generate_paths_main(rfobj, path):
                    if path.startswith(rfobj.maindir) and \
                       rfobj.maindir != os.getcwd():
                        return [rfobj.maindir]

                self.pathrules.append({
                    'prefix': '<main>',
                    'paths': generate_paths_main,
                })

            except Exception:  # pylint: disable=W0703
                pass

            # Current working directory
            self.pathrules.append({
                'prefix': '',
                'paths': lambda rfobj, path: [os.getcwd()],
            })

            if 'JENKINS_HOME' in os.environ and 'WORKSPACE' in os.environ:
                self.pathrules.append({
                    'prefix': '<jenkins>',
                    'paths': [os.environ['WORKSPACE']],
                })

            # Home directory
            self.pathrules.append({
                'prefix': '~',
                'paths': lambda rfobj, path: [os.path.expanduser('~')],
            })

            # Normalise all the paths to make them easier to compare
            for rule in self.pathrules:
                if not isinstance(rule['paths'], collections.Callable):
                    rule['paths'] = [os.path.normcase(path) for path in rule['paths']]

            # We keep a cache so that we don't have to keep regenerating the same names
            # repeatedly.
            self._cached_shortnames = {}

            # We have finally initialised this object.
            self._initialised = True

    def shortname(self, filename):
        """
        Return the shortened name, using the information collected on initialisation.
        """

        if filename in self._cached_shortnames:
            return self._cached_shortnames[filename]

        original_filename = filename

        # We have the path prefixes to apply; just step through them.
        absfilename = os.path.abspath(os.path.expanduser(filename))
        absfilename_normalised = os.path.normcase(absfilename)

        for rule in self.pathrules:
            paths = rule['paths']
            if isinstance(paths, collections.Callable):
                paths = paths(self, absfilename)
                if paths:
                    # Normalise the case of the returned paths so that we can compare.
                    paths = [os.path.normcase(path) for path in paths]
            if paths:
                for path in paths:
                    if path[-1] != os.sep:
                        path += os.sep
                    if absfilename_normalised.startswith(path):
                        prefix = rule['prefix']
                        if prefix != '':
                            prefix += os.sep
                        filename = "%s%s" % (prefix, absfilename[len(path):])
                        absfilename_normalised = filename
                        break

        filename = filename.replace('\\', '/')

        self._cached_shortnames[original_filename] = filename

        return filename


def presentation_filename(filename):
    """
    Return the filename in way that simplifies its content.

    The presentation name is reduced to make the filename easier to read in the traceback.
    """
    return ReduceFilename().shortname(filename)
