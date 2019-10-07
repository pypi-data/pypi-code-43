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
from glob import glob
from tendril.entities.edasymbols.geda import GedaSymbol
from tendril.entities.edasymbols.geda import GSymGeneratorFile

from tendril.libraries.edasymbols.base import EDASymbolLibraryBase
from tendril.libraries.edasymbols.base import EDASymbolNotFound

from tendril.config import GEDA_SYMLIB_ROOT


class GEDASymbolNotFound(EDASymbolNotFound):
    pass


class GEDASymbolLibrary(EDASymbolLibraryBase):
    _symbol_class = GedaSymbol
    _generator_class = GSymGeneratorFile
    _exc_class = GEDASymbolNotFound

    def __init__(self, *args, **kwargs):
        super(GEDASymbolLibrary, self).__init__(*args, **kwargs)
        self.subcircuits = []

    def _load_symbol(self, path,
                     resolve_generators=True,
                     include_generators=False):
        symbol = GedaSymbol(path)
        if symbol.is_generator:
            self.generators.append(symbol)
            if include_generators is True:
                self.symbols.append(symbol)
            if resolve_generators is True:
                for value in symbol.generator.values:
                    vsymbol = GedaSymbol(symbol.fpath)
                    vsymbol.is_virtual = True
                    vsymbol.value = value
                    self.symbols.append(vsymbol)
        elif symbol.is_subcircuit:
            self.subcircuits.append(symbol)
            self.symbols.append(symbol)
            # TODO This needs to be reimplemented in a cleaner form.
        else:
            self.symbols.append(symbol)
        if symbol.value.startswith('DUAL'):
            nsymbol = GedaSymbol(symbol.fpath)
            nsymbol.value = symbol.value.split(' ', 1)[1]
            self.symbols.append(nsymbol)

    def _load_folder_symbols(self, path):
        if not self._recursive:
            files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))
                     and f.endswith('.sym')]
        else:
            files = []
            for x in os.walk(path):
                for y in glob(os.path.join(x[0], '*.sym')):
                    files.append(y)

        for f in files:
            self._load_symbol(os.path.join(path, f),
                              resolve_generators=self._resolve_generators,
                              include_generators=self._include_generators)

    def _load_library(self):
        self._load_folder_symbols(self.path)

    def regenerate(self):
        self.subcircuits = []
        super(GEDASymbolLibrary, self).regenerate()

    def get_subcircuit(self, sc):
        for subcircuit in self.subcircuits:
            if subcircuit.subcircuitident == sc:
                return subcircuit

    @property
    def subcircuit_names(self):
        return [x.subcircuitident for x in self.subcircuits]

    def preconform_footprint(self, footprint):
        if footprint[0:3] == "MY-":
            footprint = footprint[3:]
        return footprint


def load(manager):
    manager.install_library('geda', GEDASymbolLibrary(GEDA_SYMLIB_ROOT))
    manager.install_exc_class('GEDASymbolNotFound', GEDASymbolNotFound)
