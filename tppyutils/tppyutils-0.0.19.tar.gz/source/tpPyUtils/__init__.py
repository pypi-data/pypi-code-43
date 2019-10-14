#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpPyUtils
"""

from __future__ import print_function, division, absolute_import

import os
import sys
import types
import pkgutil
import inspect
import traceback
import importlib
from collections import OrderedDict

logger = None


class tpPyUtils(object):
    def __init__(self):
        super(tpPyUtils, self).__init__()

        self.loaded_modules = OrderedDict()
        self.reload_modules = list()
        self._module_name = 'tpPyUtils'
        self._module_dir = self.get_module_path()
        self.logger = self.create_logger()

    def get_module_path(self):
        """
        Returns path where tpPyUtils module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import tpPyUtils
                    mod_dir = tpPyUtils.__path__[0]
                except Exception:
                    return None

        return mod_dir

    def update_paths(self):
        """
        Adds path to system paths at startup
        """

        paths_to_update = [self.externals_path()]

        for p in paths_to_update:
            if os.path.exists(p) and p not in sys.path:
                sys.path.append(p)

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
        Creates and initializes tpPyUtils logger
        """

        from tpPyUtils import log

        log_path = self.get_data_path()
        if not os.path.exists(log_path):
            raise RuntimeError('{} Log Path {} does not exists!'.format(self._module_name, log_path))

        logger = log.create_logger(logger_name=self._module_name, logger_path=log_path).logger
        if '{}_DEV'.format(self._module_name.upper()) in os.environ and os.environ.get('{}_DEV'.format(self._module_name.upper())) in ['True', 'true']:
            logger.setLevel(log.LoggerLevel.DEBUG)
        else:
            logger.setLevel(log.LoggerLevel.WARNING)

        return logger

    def externals_path(self):
        """
        Returns the paths where tpPyUtils externals packages are stored
        :return: str
        """

        return os.path.join(self.get_module_path(), 'externals')

    def import_module(self, module_name):
        """
        Static function used to import a function given its complete name
        :param module_name: str, name of the module we want to import
        """

        try:
            if '{}.externals'.format(self._module_name) in module_name:
                return
            mod = importlib.import_module(module_name)
            self.logger.debug('Imported: {}'.format(mod))
            if mod and isinstance(mod, types.ModuleType):
                return mod
        except (ImportError, AttributeError) as e:
            try:
                self.logger.warning('FAILED IMPORT: {} -> {}'.format(str(module_name), str(e)))
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

    def import_modules(self, module_path=None):
        """
        Import all the modules of the package
        :param module_path: str, base module name we want to import
        :return:
        """

        if not module_path:
            module_path = self.get_module_path()

        mod_names, mod_paths = self.explore_package(module_path=module_path, only_packages=False)
        for name, _ in zip(mod_names, mod_paths):
            if name not in self.loaded_modules.keys():
                mod = self.import_module(name)
                if mod:
                    if isinstance(mod, types.ModuleType):
                        self.loaded_modules[mod.__name__] = [os.path.dirname(mod.__file__), mod]
                        self.reload_modules.append(mod)

    def import_packages(self, module_path=None, only_packages=False, order=None, skip_packages=None):
        """
        Import all packages of a given omdule
        :param module_path: str, module name
        :param only_packages: bool, Whether to import only packages or not
        :param order: list<str>, list specifying an order for import/reload
        """

        if not skip_packages:
            skip_packages = list()

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
                mod = self.import_module(name)
                if mod:
                    if isinstance(mod, types.ModuleType):
                        self.loaded_modules[mod.__name__] = [os.path.dirname(mod.__file__), mod]
                        self.reload_modules.append(mod)

        for name, path in zip(module_names, module_paths):
            order = list()
            can_import = True
            for skip_pkg in skip_packages:
                if name.startswith(skip_pkg):
                    can_import = False
                    break
            if not can_import:
                continue
            if name in self.loaded_modules.keys():
                mod = self.loaded_modules[name][1]
                if hasattr(mod, 'order'):
                    order = mod.order
            self.import_packages(module_path=path, only_packages=False, order=order)

    def reload_all(self):
        """
        Reload all current loaded modules
        """

        for mod in list(sys.modules.keys()):
            if mod in sys.modules:
                if mod == self._module_name:
                    continue
                elif mod.startswith(self._module_name):
                    self.logger.info('Removing module: {}'.format(mod))
                    del sys.modules[mod]


def init(do_reload=True):
    """
    Initializes tpPyUtils package
    :param do_reload: bool, Whether to reload imported tpPyUtils modules or not
    :return: bool
    """

    new_importer = tpPyUtils()

    global logger
    logger = new_importer.logger

    new_importer.import_modules()
    new_importer.import_packages(only_packages=True)
    if do_reload:
        new_importer.reload_all()
