# Copyright (C) 2015 Chintalagiri Shashank
#
# This file is part of Tendril.
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
gEDA Project File
=================
"""

import os
from tendril.validation.base import ValidatableBase
from tendril.validation.base import ValidationContext
from tendril.validation.files import ExtantFile
from tendril.validation.files import FilePolicy
from tendril.validation.files import MissingFileError


class GedaProjectFile(ValidatableBase):
    def __init__(self, projfile):
        super(GedaProjectFile, self).__init__()
        self._basefolder, self.filename = os.path.split(projfile)
        self._pcbpath = None
        self.schfiles = []
        with open(projfile, 'r') as f:
            for line in f:
                line = self.strip_line(line)
                if line != '':
                    parts = line.split()
                    if parts[0].strip() == 'schematics':
                        self.schfiles = [x.strip() for x in parts[1:]]
                    if parts[0].strip() == 'output-name':
                        self._pcbpath = parts[1].strip()

    @staticmethod
    def strip_line(line):
        line = line.split("#")[0]
        return line.strip()

    @property
    def _sch_policies(self):
        vctx = self._validation_context.child('Schematic File')
        return [ExtantFile(f, self._basefolder, vctx=vctx)
                for f in self.schfiles]

    def _validate(self):
        for policy in self._sch_policies:
            policy.validate()
            self._validation_errors.add(policy.validation_errors)

        if self.pcbpath and not os.path.exists(self.pcbpath):
            vctx = self._validation_context.child('PCB File')
            pcbfilepolicy = FilePolicy(vctx, self.pcbpath, is_error=True)
            self._validation_errors.add(MissingFileError(pcbfilepolicy))
        self._validated = True

    @property
    def pcbfile(self):
        return os.path.split(self._pcbpath)[1]

    @property
    def schpaths(self):
        return [os.path.join(self._basefolder, schfile)
                for schfile in self.schfiles]

    @property
    def pcbpath(self):
        if not self._pcbpath:
            return None
        return os.path.normpath(
            os.path.join(self._basefolder, self._pcbpath + '.pcb')
        )
