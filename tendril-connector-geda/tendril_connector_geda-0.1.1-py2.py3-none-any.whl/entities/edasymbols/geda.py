#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2018 Chintalagiri Shashank
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

import os
from decimal import Decimal

from tendril.config import GEDA_SUBCIRCUITS_ROOT
from tendril.config import INSTANCE_CACHE
from tendril.config import MAKE_GSYMLIB_IMG_CACHE

from tendril.utils.fsutils import get_file_mtime
from tendril.connectors.geda.gschem import conv_gsch2png

from tendril.entities.edasymbols.base import EDASymbolBase
from tendril.entities.edasymbols.generator import EDASymbolGeneratorBase

from tendril.utils import log
logger = log.get_logger(__name__, log.INFO)


class GSymGeneratorFile(EDASymbolGeneratorBase):
    legacy_schema_name = 'gsymgenerator'
    supports_schema_name = 'gEDASymbolGenerator'
    supports_schema_version_max = Decimal('1.0')
    supports_schema_version_min = Decimal('1.0')

    def __init__(self, genpath):
        self._sympath = genpath.replace('.gen.yaml', '.sym')
        super(GSymGeneratorFile, self).__init__(genpath)

    def symbol_template(self):
        return GedaSymbol(self._sympath)


class GedaSymbol(EDASymbolBase):
    _gen_class = GSymGeneratorFile

    def __init__(self, fpath):
        """
        gEDA symbols use a symbol file, located within the gEDA component
        library folders, usually defined within a ``gafrc`` file. Only the
        symbol filename is important, and not it's location relative to the
        component library root.

        This class accepts a (full) file path to a gEDA symbol in it's
        constructor, and loads all the necessary detail abouts the symbol
        into itself.

        gEDA symbols may also represent a sub-circuit in a hierarchical
        schematic. Support for handling this type of use is included here.

        :param fpath: os path to the symbol file to be loaded
        """
        self.fpath = fpath
        self.fname = os.path.split(fpath)[1]

        self.source = ''
        self._sch_img_repr_path = None
        self._sch_img_repr_fname = None

        super(GedaSymbol, self).__init__()

    def _get_sym(self):
        self._acq_sym(self.fpath)
        if self.is_subcircuit:
            self._generate_sch_img_repr()

    def _acq_sym(self, fpath):
        _last_updated = get_file_mtime(fpath)
        with open(fpath, 'r') as f:
            for line in f.readlines():
                if line.startswith('device='):
                    self.device = line.split('=')[1].strip()
                if line.startswith('value='):
                    self.value = line.split('=')[1].strip()
                if line.startswith('footprint'):
                    self.footprint = line.split('=')[1].strip()
                    if self.footprint[0:3] == 'MY-':
                        self.footprint = self.footprint[3:]
                if line.startswith('description'):
                    self.description = line.split('=')[1].strip()
                if line.startswith('status'):
                    self.status = line.split('=')[1].strip()
                if line.startswith('package'):
                    self.package = line.split('=')[1].strip()
                if line.startswith('source'):
                    self.source = line.split('=')[1].strip()
            if self.status == '':
                self.status = 'Active'

        if self.is_generator:
            _genftime = get_file_mtime(self.genpath)
            if not _genftime or _genftime > _last_updated:
                _last_updated = _genftime
        if self.is_subcircuit:
            _schftime = get_file_mtime(self.schematic_path)
            if not _last_updated or _schftime > _last_updated:
                _last_updated = _schftime
        self.last_updated = _last_updated

    def _generate_img_repr(self):
        if not MAKE_GSYMLIB_IMG_CACHE:
            return
        outfolder = os.path.join(INSTANCE_CACHE, 'esymlib.geda')
        self._img_repr_path = os.path.join(outfolder, self.img_repr_fname)
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        if os.path.exists(self._img_repr_path):
            if get_file_mtime(self._img_repr_path) > get_file_mtime(self.fpath):  # noqa
                return
        conv_gsch2png(self.fpath, outfolder)

    def _generate_sch_img_repr(self):
        if not MAKE_GSYMLIB_IMG_CACHE:
            return
        outfolder = os.path.join(INSTANCE_CACHE, 'esymlib.geda')
        self._sch_img_repr_fname = self.source + '.png'
        self._sch_img_repr_path = os.path.join(outfolder,
                                               self._sch_img_repr_fname)
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)
        if os.path.exists(self._sch_img_repr_path):
            if get_file_mtime(self._sch_img_repr_path) > get_file_mtime(self.schematic_path):  # noqa
                return
        conv_gsch2png(self.schematic_path, outfolder, include_extension=True)

    # Validation
    def _symbol_validate(self):
        # TODO Migrate to ValidatableBase
        if self.is_subcircuit:
            if not self.source.endswith('.sch'):
                return False
            if not os.path.exists(self.schematic_path):
                return False
            return True
        return super(GedaSymbol, self)._symbol_validate()

    # Subcircuits
    @property
    def is_subcircuit(self):
        if self.source != '':
            return True
        return False

    @property
    def schematic_path(self):
        if not self.is_subcircuit:
            raise AttributeError
        return os.path.join(GEDA_SUBCIRCUITS_ROOT, self.source)

    @property
    def schematic_fname(self):
        if not self.is_subcircuit:
            raise AttributeError
        return self.source

    @property
    def subcircuitident(self):
        if not self.is_subcircuit:
            raise AttributeError
        return os.path.splitext(self.fname)[0]

    @property
    def sch_img_repr_fname(self):
        return self._sch_img_repr_fname

    @property
    def gname(self):
        return self.fname

    @property
    def gpath(self):
        return self.fpath
