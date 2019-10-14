#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains basic class for Python importers
"""


from __future__ import print_function, division, absolute_import

import os
import sys
import types
import pkgutil
import traceback
import importlib
from collections import OrderedDict

from tpPyUtils import decorators, log as log_utils


class Importer(object):
    """
    Base class that allows to import/reload all the modules in a given package and in a given order
    """

    def __init__(self, module_name, module_dir=None, logger=None):
        super(Importer, self).__init__()

        if module_dir is None:
            module_dir = self.get_module_path()

        self._module_name = module_name
        self._module_dir = module_dir

        self.loaded_modules = OrderedDict()
        self.reload_modules = list()

        if logger is None:
            self.log, self.logger = self.create_logger()
        else:
            self.log = None
            self.logger = logger

    @decorators.abstractmethod
    def get_module_path(self):
        """
        Returns path where importer is located
        Must be override in class
        """

        raise NotImplementedError('get_module_path() is not implemented!')

    def get_data_path(self):
        """
        Returns path where user data should be located
        :return: str
        """

        data_path = os.path.join(os.getenv('APPDATA'), self._module_name)
        if not os.path.isdir(data_path):
            os.makedirs(data_path)

        return data_path

    def create_logger(self):
        """
        Creates and initializes importer logger
        """

        log_path = self.get_data_path()
        if not os.path.exists(log_path):
            raise RuntimeError('{} Log Path {} does not exists!'.format(self._module_name, log_path))

        log = log_utils.create_logger(logger_name=self._module_name, logger_path=log_path)
        logger = log.logger

        if '{}_DEV'.format(self._module_name.upper()) in os.environ and os.environ.get('{}_DEV'.format(self._module_name.upper())) in ['True', 'true']:
            logger.setLevel(log_utils.LoggerLevel.DEBUG)
        else:
            logger.setLevel(log_utils.LoggerLevel.WARNING)

        return log, logger

    def import_module(self, module_name):
        """
        Static function used to import a function given its complete name
        :param module_name: str, name of the module we want to import
        """

        try:
            mod = importlib.import_module(module_name)
            self.logger.debug('Imported: {}'.format(mod))
            if mod and isinstance(mod, types.ModuleType):
                return mod
        except Exception as e:
            try:
                self.logger.warning('FAILED IMPORT: {} -> {}'.format(str(module_name), str(traceback.format_exc())))
            except Exception:
                self.logger.warning('FAILED IMPORT: {}'.format(module_name))
            self.logger.debug('\t>>>{}'.format(traceback.format_exc()))

    def explore_package(self, module_path, only_packages=False):
        """
        Load module iteratively
        :param module_path: str, name of the module
        :param only_packages: bool, Whether is only packages need to be checked or not
        :return: list<str>, list<str>, list of loaded modules names and list loaded moule paths
        """

        module_names = list()
        module_paths = list()

        def foo(name, only_packages):
            for importer, m_name, is_pkg in pkgutil.iter_modules([name]):
                mod_path = name + '\\' + m_name
                mod_name = '{}.'.format(self._module_name) + os.path.relpath(mod_path, self._module_dir).replace('\\', '.')
                if only_packages:
                    if is_pkg:
                        module_paths.append(mod_path)
                        module_names.append(mod_name)
                else:
                    module_paths.append(mod_path)
                    module_names.append(mod_name)
        foo(name=module_path, only_packages=only_packages)

        return module_names, module_paths

    def import_modules(self, module_path=None, skip_modules=None):
        """
        Import all the modules of the package
        :param module_path: str, base module name we want to import
        :param skip_modules: list(str)
        :return:
        """

        if skip_modules is None:
            skip_modules = list()

        if not module_path:
            module_path = self.get_module_path()

        mod_names, mod_paths = self.explore_package(module_path=module_path, only_packages=False)
        for name, _ in zip(mod_names, mod_paths):
            if name not in self.loaded_modules.keys():
                if name in skip_modules:
                    continue
                mod = self.import_module(name)
                if mod:
                    if isinstance(mod, types.ModuleType):
                        self.loaded_modules[mod.__name__] = [os.path.dirname(mod.__file__), mod]
                        self.reload_modules.append(mod)

    def import_packages(self, module_path=None, only_packages=False, order=None, skip_modules=None):
        """
        Import all packages of a given omdule
        :param module_path: str, module name
        :param only_packages: bool, Whether to import only packages or not
        :param order: list<str>, list specifying an order for import/reload
        """

        if skip_modules is None:
            skip_modules = list()

        if not module_path:
            module_path = self.get_module_path()

        package_names, package_paths = self.explore_package(module_path=module_path, only_packages=only_packages)

        if order is None:
            order = list()

        ordered_names = list()
        ordered_paths = list()
        temp_index = 0
        i = -1
        for o in order:
            for n, p in zip(package_names, package_paths):
                if str(n) == str(o):
                    i += 1
                    temp_index = i
                    ordered_names.append(n)
                    ordered_paths.append(p)
                elif n.endswith(o):
                    ordered_names.insert(temp_index + 1, n)
                    ordered_paths.insert(temp_index + 1, n)
                    temp_index += 1
                elif str(o) in str(n):
                    ordered_names.append(n)
                    ordered_paths.append(p)

        ordered_names.extend(package_names)
        ordered_paths.extend(package_paths)

        names_set = set()
        paths_set = set()
        module_names = [x for x in ordered_names if not (x in names_set or names_set.add(x))]
        module_paths = [x for x in ordered_paths if not (x in paths_set or paths_set.add(x))]

        reloaded_names = list()
        reloaded_paths = list()
        for n, p in zip(package_names, package_paths):
            reloaded_names.append(n)
            reloaded_paths.append(p)

        for name, _ in zip(module_names, module_paths):
            if name not in self.loaded_modules.keys():
                skip = False
                for skip_module in skip_modules:
                    if skip_module == name or name.startswith(skip_module):
                        skip = True
                        break
                if skip:
                    continue
                mod = self.import_module(name)
                if mod:
                    if isinstance(mod, types.ModuleType):
                        self.loaded_modules[mod.__name__] = [os.path.dirname(mod.__file__), mod]
                        self.reload_modules.append(mod)

        for name, path in zip(module_names, module_paths):
            order = list()
            if name in self.loaded_modules.keys():
                mod = self.loaded_modules[name][1]
                if hasattr(mod, 'order'):
                    order = mod.order
            self.import_packages(module_path=path, only_packages=False, order=order, skip_modules=skip_modules)

    def reload_all(self):
        """
        Reload all current loaded modules
        """

        for mod in self.reload_modules:
            if not hasattr(mod, 'no_reload'):
                self.logger.info('Reloading: {}'.format(mod.__name__))
                reload(mod)
            else:
                self.logger.info('Avoiding reload of: {}'.format(mod.__name__))
        self.logger.debug('{} reloaded successfully!'.format(self._module_name))


class SimpleImporter(object):
    """
    Simple importer in which module order cannot be defined useful in some scenarios
    """

    def __init__(self, module_name, logger=None):
        super(SimpleImporter, self).__init__()

        self._module_name = module_name

        if logger is None:
            self.log, self.logger = self.create_logger()
        else:
            self.log = None
            self.logger = logger

    @decorators.abstractmethod
    def get_module_path(self):
        """
        Returns path where importer is located
        Must be override in class
        """

        raise NotImplementedError('get_module_path() is not implemented!')

    def get_data_path(self):
        """
        Returns path where user data should be located
        :return: str
        """

        data_path = os.path.join(os.getenv('APPDATA'), self._module_name)
        if not os.path.isdir(data_path):
            os.makedirs(data_path)

        return data_path

    def create_logger(self):
        """
        Creates and initializes importer logger
        """

        log_path = self.get_data_path()
        if not os.path.exists(log_path):
            raise RuntimeError('{} Log Path {} does not exists!'.format(self._module_name, log_path))

        log = log_utils.create_logger(logger_name=self._module_name, logger_path=log_path)
        logger = log.logger

        if '{}_DEV'.format(self._module_name.upper()) in os.environ and os.environ.get('{}_DEV'.format(self._module_name.upper())) in ['True', 'true']:
            logger.setLevel(log_utils.LoggerLevel.DEBUG)
        else:
            logger.setLevel(log_utils.LoggerLevel.WARNING)

        return log, logger

    def import_modules(self):
        """
        This function imports all the modules located in the given importer directory
        """

        import inspect
        scripts_dir = self.get_module_path()
        for key, module in sys.modules.items():
            try:
                module_path = inspect.getfile(module)
            except TypeError:
                continue
            if module_path == scripts_dir:
                continue
            if module_path.startswith(scripts_dir):
                try:
                    importlib.import_module(module.__name__)
                except Exception as e:
                    self.logger.error('{} | {}'.format(e, traceback.format_exc()))

    def reload_all(self):
        """
        Reloads all the modules of the given importer module name
        """

        for mod in sys.modules.keys():
            if mod in sys.modules and mod.startswith(self._module_name):
                del sys.modules[mod]
        self.import_modules()


def init_importer(importer_class, do_import=False, do_reload=True):
    """
    Initializes importer
    :param importer_class:
    :param do_import: bool
    :param do_reload: bool
    :return:
    """

    new_importer = importer_class()
    if do_reload:
        new_importer.reload_all()

    if do_import:
        new_importer.import_modules()
        if hasattr(importer_class, 'import_packages'):
            new_importer.import_packages(only_packages=True)

    return new_importer