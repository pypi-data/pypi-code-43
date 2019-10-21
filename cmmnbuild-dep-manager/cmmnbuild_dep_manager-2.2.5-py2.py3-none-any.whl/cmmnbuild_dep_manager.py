# -*- coding: utf-8 -*-
'''CommonBuild Dependency Manager

Copyright (c) CERN 2015-2017

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors:
    T. Levens       <tom.levens@cern.ch>
    R. De Maria     <riccardo.de.maria@cern.ch>
    M. Hostettler   <michi.hostettler@cern.ch>
'''

from contextlib import contextmanager
import glob
import importlib
import json
import logging
import os
import pickle
import shutil
import site
import six
import zipfile


class Manager(object):
    def __init__(self, pkg=None, lvl=None):
        logging.basicConfig()
        self.log = logging.getLogger(__package__)
        if lvl is not None:
            self.log.setLevel(lvl)
        self._setup_resolver()
        needs_installation = pkg is not None and not self.is_installed(pkg)
        if needs_installation:
            # Temporarily set the log level to notify the user that this could
            # take some time.
            with self._tmp_set_logging_level('INFO'):
                self.log.info(
                    'Package "{0}" is not yet set up - installing and '
                    'resolving JARs'.format(pkg))
                self.install(pkg)

    def set_logging_level(self, lvl):
        '''Set the logging level'''
        self.log.setLevel(lvl)

    @contextmanager
    def _tmp_set_logging_level(self, lvl):
        orig_level = self.log.level
        self.log.setLevel(lvl)
        yield
        self.log.setLevel(orig_level)

    def help(self, method='__init__'):
        '''Print the docstring for a method'''
        print(getattr(self, method).__doc__)

    def jar_path(self):
        '''Return the directory containing the resolved jars'''
        return os.path.join(self._dir(), 'lib')

    def jars(self):
        '''Return a list of the resolved jars'''
        if os.path.isdir(self.jar_path()):
            return [
                os.path.join(self.jar_path(), f)
                for f in os.listdir(self.jar_path())
                if f.lower().endswith('.jar')
            ]
        else:
            return []

    def class_list(self):
        '''List all classes in the resolved jars'''
        return sorted(self._class_data().keys())

    def class_hints(self, class_name):
        '''Print code hints for using a Java class from Python code

        Usage::

            mgr = cmmnbuild_dep_manager.Manager()
            jpype = mgr.start_jpype_jvm()
            print(mgr.class_hints('Fidel'))

        '''
        names = sorted(self.class_search(class_name))
        roots = set()
        for name in names:
            parts = name.split('.')
            cname = parts[-1]
            root = parts[0]
            if root not in roots:
                print('{0} = jpype.JPackage(\'{0}\')'.format(root))
                roots.add(root)
            print('{0} = {1}'.format(cname, name))

    def class_search(self, class_name):
        '''Search for Java classes by name'''
        return list(filter(lambda x: class_name in x, self.class_list()))

    def class_path(self, extra_jars=[]):
        '''Returns a delimited string suitable for java.class.path'''
        jars = self.jars()
        jars.extend(extra_jars)
        jars.append(os.getcwd())
        return ';'.join(jars) if os.name == 'nt' else ':'.join(jars)

    def _class_data(self):
        '''List all classes in the resolved jars'''
        classes = {}
        for jar in self.jars():
            jarname, jarversion = self._get_jarversion(jar)
            names = zipfile.ZipFile(jar).namelist()
            for name in names:
                if name.endswith('.class'):
                    classname = name[:-6].replace('/', '.')
                    classes.setdefault(classname, []).append((
                        jarname, jarversion
                    ))
        return classes

    def _get_jarversion(self, jar):
        return os.path.splitext(os.path.basename(jar))[0].rsplit('-', 1)

    def class_doc(self, obj_or_string):
        '''Return URLs of the documentation and source code of a class

        Example:

        import pjlsa
        lsa=pjlsa.LSAClient()
        pjlsa.mgr.class_doc(lsa._contextService)

        '''
        import jpype
        if isinstance(obj_or_string, six.string_types):
            classname = obj_or_string
        elif hasattr(obj_or_string, 'getProxiedInterfaces'):
            classname = obj_or_string.getProxiedInterfaces()[0].__name__
        elif isinstance(obj_or_string, jpype._jclass._MetaClassForMroOverride):
            classname = obj_or_string.__name__
        else:
            classname = obj_or_string.__class__.__name__
        if classname not in self.class_list():
            classnames = self.class_search(classname)
            if not classnames:
                raise ValueError('Could not find class {0}'.format(classname))
        else:
            classnames = [classname]
        classnames = set(map(lambda x: x.split('$')[0], classnames))
        self._resolver.get_help(classnames, self._class_data())

    def start_jpype_jvm(self, extra_jars=[]):
        '''Starts a new JPype JVM with the appropriate class path'''
        import jpype
        if not jpype.isJVMStarted():
            self.log.info(
                'starting a JPype JVM with {0} jars from {1}'.format(
                    len(self.jars()),
                    self.jar_path()
                )
            )
            javalibpath = os.environ.get('JAVA_JVM_LIB')
            if javalibpath is None:
                javalibpath = jpype.getDefaultJVMPath()
            jpype.startJVM(
                javalibpath,
                '-Xss2m',   # Required for kernels patching CVE-2017-1000364
                '-Xrs',     # Needed for proper handling of KeyboardInterrupt
                '-Djava.class.path={0}'.format(self.class_path(extra_jars))
            )
            java_version = jpype.java.lang.System.getProperty('java.version')
            if not java_version.startswith('1.8') and not java_version.startswith('11.'):
                raise OSError('Java version must be equal to 1.8: {0} is {1}.'.format(
                    javalibpath, java_version
                ))
        else:
            self.log.warning('JVM is already started')
        return jpype

    def _user_dir(self):
        '''Returns the module directory in the usersitepackages'''
        if hasattr(site, 'getusersitepackages'):
            return os.path.join(site.getusersitepackages(), __package__)
        else:
            # running in VirtualEnv - path in __package__ will be absolute
            return __package__

    def _dist_dir(self):
        '''Returns the module directory in the distribution'''
        return os.path.dirname(__file__)

    def _dir(self):
        '''Returns the module directory'''
        if os.path.isdir(self._user_dir()):
            return self._user_dir()
        else:
            return self._dist_dir()

    def _load_modules(self):
        '''Load modules data from modules.json

        Returns a dictionary of the form:

            {'name': 'version', ...}

        Where 'name' is the module name and 'version' is the version of the
        module for which the jars were downloaded for. Version will be an empty
        string if the module has been registered but not downloaded.
        '''
        modules = {}

        # Load pickled 'modules' files created by versions < 2.0.0
        old_mod_files = (
            os.path.join(self._dist_dir(), 'modules'),
            os.path.join(self._user_dir(), 'modules')
        )
        for f in old_mod_files:
            if os.path.isfile(f):
                self.log.debug('loading {0}'.format(f))
                with open(f, 'rb') as fp:
                    pkl_data = pickle.load(fp)
                    for k in pkl_data:
                        modules[k] = ''

        # Load json 'modules.json' files created by version >= 2.0.0
        mod_files = (
            os.path.join(self._dist_dir(), 'modules.json'),
            os.path.join(self._user_dir(), 'modules.json')
        )
        for f in mod_files:
            if os.path.isfile(f):
                self.log.debug('loading {0}'.format(f))
                with open(f, 'r') as fp:
                    json_data = json.load(fp)
                    for k, v in json_data.items():
                        modules[k] = v

        return modules

    def _save_modules(self, modules):
        '''Save modules data to modules.json'''
        user_dir = self._user_dir()
        dist_dir = self._dist_dir()
        if os.path.isdir(user_dir):
            save_dir = user_dir
        elif os.access(dist_dir, os.W_OK | os.X_OK):
            save_dir = dist_dir
        else:
            self.log.info('creating directory {0}'.format(user_dir))
            os.makedirs(user_dir)
            save_dir = user_dir
        mod_file = os.path.join(save_dir, 'modules.json')
        self.log.debug('saving {0}'.format(mod_file))
        with open(mod_file, 'w') as fp:
            json.dump(modules, fp)

        # Remove 'modules' file used by versions < 2.0.0
        old_modules = os.path.join(save_dir, 'modules')
        if os.path.isfile(old_modules):
            self.log.warning('removing obsolete file {0}'.format(old_modules))
            os.remove(old_modules)

    def _setup_resolver(self, override=None):
        from .resolver import resolvers
        for resolver in resolvers():
            if resolver.is_available() and (override is None or resolver.__name__ == override):
                self._resolver = resolver
                self.log.info('using resolver: {0} ({1})'.format(resolver.__name__, resolver.description))
                break

    def _find_supported_resolvers(self, module):
        supported_resolvers = []
        from .resolver import resolvers
        for resolver in resolvers():
            try:
                deps = list(getattr(module, resolver.dependency_variable))
                if deps is not None:
                    supported_resolvers.append(resolver)
            except:
                pass
        return supported_resolvers

    def _find_module_info(self, module_name):
        module = importlib.import_module(module_name)

        # Check __***_deps__ exists
        deps = []
        try:
            deps = list(getattr(module, self._resolver.dependency_variable))
        except:
            pass

        if not deps:
            supported_resolvers = self._find_supported_resolvers(module)
            supported_resolvers_explanation = ''
            if supported_resolvers:
                supported_resolvers_explanation = '\nResolvers compatible with this module:\n{}'.format(
                    ', '.join([' - {0} [{1}] - {2}'.format(r.__name__, r.dependency_variable, r.description)
                               for r in supported_resolvers]))
            raise AttributeError('module {0} does not declare {1}, which is needed for {2} ({3}) {4}'
                                 .format(module_name, self._resolver.dependency_variable,
                                         self._resolver.__name__, self._resolver.description,
                                         supported_resolvers_explanation))

        # Check __version__ exists
        version = module.__version__
        return version, deps

    def register(self, *args):
        '''Register one or more modules'''
        ret = []
        modules = self._load_modules()
        for name in args:
            try:
                version, deps = self._find_module_info(name)

                if name not in modules.keys() or modules[name] != version:
                    modules[name] = ''
                    self.log.info('{0} registered'.format(name))
                    ret.append(name)
            except ImportError:
                self.log.error(
                    '{0} not found'.format(name)
                )
            except Exception as e:
                self.log.error(e)
        if ret:
            self._save_modules(modules)
        return tuple(ret)

    def unregister(self, *args):
        '''Unregister one or more modules'''
        ret = []
        modules = self._load_modules()
        for name in args:
            if name in modules.keys():
                del modules[name]
                self.log.info('{0} unregistered'.format(name))
                ret.append(name)
        if ret:
            self._save_modules(modules)
        return tuple(ret)

    def install(self, *args):
        '''Register one or more modules and resolve dependencies'''
        ret = self.register(*args)
        if ret:
            self.resolve()
        return ret

    def uninstall(self, *args):
        '''Unregister one or more modules and resolve dependencies'''
        ret = self.unregister(*args)
        if ret:
            self.resolve()
        return ret

    def is_registered(self, name):
        '''Check if module is registered'''
        modules = self._load_modules()
        return name in modules.keys()

    def is_installed(self, name, version=None):
        '''Check if module is installed'''
        modules = self._load_modules()
        if name in modules.keys():
            try:
                if version is None:
                    version, _ = self._find_module_info(name)
                if modules[name] == version:
                    return True
            except:
                pass
        return False

    def list(self):
        '''Returns a list of the currently registered modules'''
        return sorted(self._load_modules().keys())

    def resolve(self, force_resolver=None):
        '''Resolve dependencies for all registered modules using CBNG'''
        if force_resolver is not None:
            self._setup_resolver(force_resolver)
        self.log.info('resolving dependencies')
        self.log.debug('lib directory is {0}'.format(self.jar_path()))

        all_dependencies = []
        modules = self._load_modules()

        # Build the dependency list from all installed packages
        for name, vers in modules.items():
            try:
                version, deps = self._find_module_info(name)
                all_dependencies.extend(deps)
                modules[name] = version
            except ImportError:
                self.log.error('{0} not found'.format(name))
                self.unregister(name)
            except Exception as e:
                self.log.error(e)

        self._save_modules(modules)

        try:
            # shutdown JVM to be able to replace the JARs (on windows at least)
            import jpype
            jpype.shutdownJVM()
        except:
            pass

        if not all_dependencies:
            self.log.error('no dependencies were found')
            return

        resolver = self._resolver(all_dependencies)
        self.log.info('resolved {0} using {1}'.format(all_dependencies, resolver))

        # Create user directory if dist directory is not writeable
        if not os.access(self._dist_dir(), os.W_OK | os.X_OK):
            if not os.path.exists(self._user_dir()):
                self.log.info('creating directory {0}'.format(
                    self._user_dir())
                )
                os.makedirs(self._user_dir())

        # ensure the jar destination directory exists
        if not os.path.exists(self.jar_path()):
            self.log.info('creating JAR directory {0}'.format(
                self.jar_path())
            )
            os.makedirs(self.jar_path())

        # Remove 'jars' directory used by versions < 2.0.0
        old_jars_dir = os.path.join(self._dir(), 'jars')
        if os.path.isdir(old_jars_dir):
            self.log.warning('removing obsolete directory {0}'.format(
                old_jars_dir
            ))
            shutil.rmtree(old_jars_dir)

        # Remove exisiting jars
        old_jars = glob.glob(os.path.join(self.jar_path(), '*.jar'))
        self.log.info('removing {0} jars from {1}'.format(
            len(old_jars), self.jar_path()
        ))
        for jar in old_jars:
            os.remove(jar)

        # Deploy new jars
        resolver.save_jars(self.jar_path())
