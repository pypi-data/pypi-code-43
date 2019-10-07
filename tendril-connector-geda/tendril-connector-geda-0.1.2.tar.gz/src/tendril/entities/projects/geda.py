#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2019 Chintalagiri Shashank
#
# This file is part of tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
gEDA Project Configuration Schema
---------------------------------
"""

import os
from decimal import Decimal

from tendril.connectors.geda.projfile import GedaProjectFile
from tendril.entities.projects.eda import EDAProjectConfig
from tendril.entities.projects.config import NoProjectError
from tendril.validation.files import ExtantFile


class NoGedaProjectError(NoProjectError):
    pass


class gEDAProjectConfig(EDAProjectConfig):
    legacy_schema_name = 'pcbconfigs'
    supports_schema_name = 'gEDAProjectConfig'
    supports_schema_version_max = Decimal('1.0')
    supports_schema_version_min = Decimal('1.0')
    FileNotFoundExceptionType = NoGedaProjectError
    configs_location = ['schematic', 'configs.yaml']

    def __init__(self, *args, **kwargs):
        self._projfile_obj = None
        super(gEDAProjectConfig, self).__init__(*args, **kwargs)

    def elements(self):
        e = super(gEDAProjectConfig, self).elements()
        e.update({
            '_projfile': self._p('projfile', required=True,
                                 parser=ExtantFile,
                                 parser_args={'basedir': self.basefolder})
        })
        return e

    @property
    def projfile(self):
        if not self._projfile_obj:
            self._projfile_obj = GedaProjectFile(self._projfile.filepath)
            self._projfile_obj.validate()
            self._validation_errors.add(self._projfile_obj.validation_errors)
        return self._projfile_obj

    @property
    def pcbpath(self):
        return self.projfile.pcbpath

    @property
    def schpaths(self):
        return self.projfile.schpaths

    def _process(self):
        super(gEDAProjectConfig, self)._process()
        _ = self.projfile

    @property
    def _pcb_allowed(self):
        if os.path.split(self.basefolder)[1] == 'schematic':
            return True
        else:
            return False
