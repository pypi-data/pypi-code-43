# -*- coding: utf-8 -*-
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError


class Cesionario():

    def __init__(self, vals):
        util.set_fset_from_keysrom_keys(self, vals)

        def RUT(self):
            return self._rut

        def RazonSocial(self, val):
            self._razon_social = self._acortar_str(val, 100)

        def Direccion(self, val):
            self._direccion = self._acortar_str(val, 70)

        def eMail(self):
            return self._email
