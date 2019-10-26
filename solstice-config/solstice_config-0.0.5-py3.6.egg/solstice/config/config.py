#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains settings implementation for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import artellapipe.config as artella_cfg

import os
import inspect


class SolsticeConfigs(artella_cfg.ArtellaConfigs, object):

    def get_configurations_path(self):
        """
        Overrides base ArtellaConfigs get_configurations_path function
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
                    import artellapipe
                    mod_dir = artellapipe.__path__[0]
                except Exception:
                    return None

        return mod_dir
