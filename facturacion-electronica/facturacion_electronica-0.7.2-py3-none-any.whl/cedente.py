# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError


class Cedente(object):

    def __init__(self, vals):
        util.set_fset_from_keysrom_keys(self, vals)

    def RUT(self):
        return self._rut

    def Nombre(self):
        return self._nombre

