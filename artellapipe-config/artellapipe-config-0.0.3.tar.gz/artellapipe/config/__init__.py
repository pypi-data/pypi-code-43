#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for artellapipe-config
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import inspect

from tpPyUtils import path as path_utils


class ArtellaConfigs(object):

    CHANGELOG_FILE_NAME = 'changelog.yml'
    CONFIG_FILE_NAME = 'config.yml'
    NAMING_FILE_NAME = 'naming.yml'

    def get_configurations_path(self):
        """
        Returns path where tpNameIt module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import tpDccLib
                    mod_dir = tpDccLib.__path__[0]
                except Exception:
                    return None

        return mod_dir

    def get_changelog_file(self):
        """
        Returns path where changelog file is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(self.get_configurations_path(), self.CHANGELOG_FILE_NAME))

    def get_project_configuration_file(self):
        """
        Returns path where project configuration file is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(self.get_configurations_path(), self.CONFIG_FILE_NAME))

    def get_naming_file(self):
        """
        Returns path where naming rules file is located
        :return: str
        """

        return path_utils.clean_path(os.path.join(self.get_configurations_path(), self.NAMING_FILE_NAME))
