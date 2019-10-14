#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Config definition
"""

from __future__ import print_function, division, absolute_import

import os
import subprocess
import platform
import configparser

from tpPyUtils import osplatform


class Config(configparser.RawConfigParser, object):
    """
    Configuration file
    """

    EXCLUDE_PATTERNS = ['__*', '*.']
    ICON_EXTENSIONS = ['xpm', 'png', 'bmp', 'jpeg']

    def __init__(self, app_name, root_folder=None, config_name='config', config_extension='ini', *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        self._app_name = app_name.replace(' ', '_').lower()

        if root_folder:
            self.config_file = os.path.join(osplatform.get_system_config_directory(), root_folder, self._app_name, '{}.{}'.format(config_name, config_extension))
        else:
            self.config_file = os.path.join(osplatform.get_system_config_directory(), self._app_name, '{}.{}'.format(config_name, config_extension))

        print('{0}: Configuration File: {1}'.format(self._app_name, self.config_file))
        try:
            self.readfp(open(self.config_file, 'r'))
            print('{0}: Configuration File read successfully!'.format(self._app_name))
        except IOError:
            print('{0}: Configuration file not found! Creating it...'.format(self._app_name))
            self._create()

    @property
    def app_name(self):
        return self._app_name

    @staticmethod
    def create_config(app_name, root_folder=None):
        """
        Construct the configuration object from necessary elements
        """

        config = Config(app_name=app_name, root_folder=root_folder, allow_no_value=True)

        return config

    def _create(self):
        """
        If configuration file is not already created we create it
        """

        print('Initializing {0} Settings, creating configuration file: {1}\n'.format(self._app_name, self.config_file))

        self.add_section(self._app_name)

        if not os.path.exists(os.path.dirname(self.config_file)):
            try:
                print('Creating Settings Folder: {}'.format(os.path.dirname(self.config_file)))
                original_umask = os.umask(0)
                os.makedirs(os.path.dirname(self.config_file), 0o770)
            finally:
                os.umask(original_umask)
        f = open(self.config_file, 'w')
        f.close()
        self.update()

        print('{0} has successfully created a new configuration file at: {1}\n'.format(self._app_name, str(self.config_file)))

    def update(self):
        with open(self.config_file, 'wb') as f:
            self.write(f)

    def get(self, option, section=None):

        if not section:
            section = self._app_name

        try:
            return configparser.RawConfigParser.get(self, section, option)
        except configparser.NoOptionError:
            return ''

    def get_list(self, option, section=None):
        """
        Convert string value to list object
        """

        if not section:
            section = self._app_name

        if self.has_option(section, option):
            return self.get(section=section, option=option).replace(' ', '').split(',')
        else:
            raise KeyError('{0} with {1} does not exist!'.format(section, option))

    def edit(self):
        """
        Edit file with default OS application
        """

        if platform.system().lower() == 'windows':
            os.startfile(str(self.config_file))
        else:
            if platform.system().lower() == 'darwin':
                call = 'open'
            else:
                call = 'xdg-open'
            subprocess.call(call, self.config_file)
