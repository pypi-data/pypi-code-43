# -*- coding: utf-8 -*-
from facturacion_electronica.cedente import Cedente as Ced
from facturacion_electronica.cesionario import Cesionario as Ces
from facturacion_electronica.documento import Documento
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError
from lxml import etree
import base64
import collections


class Cesion(Documento):

    def __init__(self, vals):
        util.set_fset_from_keysrom_keys(self, vals)

    @property
    def SecCesion(self):
        if not hasattr(self, '_sec_cesion'):
            return False

    @property
    def Cedente(self):
        Emisor = collections.OrderedDict()
        Emisor['RUT'] = self.Emisor.RUTEmisor
        Emisor['RazonSocial'] = self.Emisor.RznSoc
        Emisor['Direccion'] = self.Emisor.Direccion
        Emisor['eMail'] = self.Emisor.CorreoEmisor
        Emisor['RUTAutorizado'] = collections.OrderedDict()
        Emisor['RUTAutorizado']['RUT'] = self.Cedente.RUT
        Emisor['RUTAutorizado']['Nombre'] = self.Cedente.Nombre
        Emisor['DeclaracionJurada'] = self.DeclaracionJurada
        return Emisor

    @Cedente.setter
    def Cedente(self, vals):
        self._cedente = Ced(vals)

    @property
    def Cesionario(self):
        Receptor = collections.OrderedDict()
        if not self.Cesionario or not self.Cesionario.RUT:
            raise UserError("Debe Ingresar RUT Cesionario")
        Receptor['RUT'] = self.Cesionario.RUT
        Receptor['RazonSocial'] = self.Cesionario.RazonSocial
        Receptor['Direccion'] = self.Cesionario.Direccion
        Receptor['eMail'] = self.Cesionario.eMail
        return Receptor

    @Cesionario.setter
    def Cesionario(self, vals):
        self._cesionario = Ces(vals)

    @property
    def DeclaracionJurada(self):
        if not hasattr(self, '_declaracion_jurada'):
            return  u'''Se declara bajo juramento que {0}, RUT {1} \
ha puesto a disposicion del cesionario {2}, RUT {3}, el o los documentos donde constan los recibos de las mercaderías entregadas o servicios prestados, \
entregados por parte del deudor de la factura {4}, RUT {5}, de acuerdo a lo establecido en la Ley No. 19.983'''.format(
                self.Emisor.Nombre,
                self.Emisor.Rut,
                self.Cesionario.Nombre,
                self.Cesionario.RUT,
                self.Receptor.Nombre,
                self.Receptor.RUT,
            )
        return self._declaracion_jurada

    @DeclaracionJurada.setter
    def DeclaracionJurada(self, val):
        self._declaracion_jurada = val

    @property
    def ID(self):
        if not hasattr(self, '_id'):
            return "DocCed_%s" % str(self.Folio)
        return self._id

    @ID.setter
    def ID(self, val):
        self._id = val

    @property
    def IdDTE(self):
        IdDoc = collections.OrderedDict()
        IdDoc['TipoDTE'] = self.TipoDTE
        IdDoc['RUTEmisor'] = self.Emisor.RUTEmisor
        if not self.Receptor.RUTReceptor:
            raise UserError("Debe Ingresar RUT Receptor")
        IdDoc['RUTReceptor'] = self.Receptor.RUTReceptor
        IdDoc['Folio'] = self.Folio
        IdDoc['FchEmis'] = self.FchEmis
        IdDoc['MntTotal'] = self.MntTotal
        return IdDoc

    @property
    def ImageAR(self):
        if not hasattr(self, 'imagenes'):
            return []
        return self._imagenes

    @property
    def MontoCesion(self):
        if not hasattr(self, '_monto_cesion'):
            return 0
        return self._monto_cesion

    @MontoCesion.setter
    def MontoCesion(self, val):
        self._monto_cesion = val

    @property
    def UltimoVencimiento(self):
        return True

    @UltimoVencimiento.setter
    def UltimoVencimiento(self, val):
        self._ultimo_vencimiento = val

    @property
    def xml_dte(self):
        if not hasattr(self, '_xml_dte'):
            return False
        return self._xml_dte

    @xml_dte.setter
    def xml_dte(self, val):
        self._xml_dte = val

    def doc_cedido(self):
        xml = '''<DocumentoDTECedido ID="{0}">
{1}
<TmstFirma>{2}</TmstFirma>
</DocumentoDTECedido>
    '''.format(
            self.ID,
            self.xml_dte,
            util.time_stamp(),
        )
        return xml

    def _dte_cedido(self):
        doc = self.doc_cedido()
        xml = '''<DTECedido xmlns="http://www.sii.cl/SiiDte" version="1.0">
{}
</DTECedido>'''.format(doc)
        return xml

    def _crear_info_trans_elec_aec(self, doc, id):
        xml = '''<DocumentoCesion ID="{0}">
{1}
</DocumentoCesion>
'''.format(
            id,
            doc,
        )
        return xml

    def _crear_info_cesion(self, doc):
        xml = '''<Cesion xmlns="http://www.sii.cl/SiiDte" version="1.0">
{1}
</Cesion>
'''.format(
            id,
            doc,
        )
        return xml

    def xml_doc_cedido(self):
        data = collections.OrderedDict()
        data['SeqCesion'] = self.SeqCesion
        data['IdDTE'] = self.IdDTE
        data['Cedente'] = self.Cedente
        data['Cesionario'] = self.Cesionario
        data['MontoCesion'] = self.MontoCesion
        data['UltimoVencimiento'] = self.UltimoVencimiento
        data['TmstCesion'] = util.time_stamp()
        xml = self._dte_to_xml(data)
        doc_cesion_xml = self._crear_info_trans_elec_aec(xml, id)
        cesion_xml = self._crear_info_cesion(doc_cesion_xml)
        root = etree.XML(cesion_xml)
        xml_formated = etree.tostring(root).decode()
        cesion = self.firmar(
            xml_formated,
            'CesDoc1',
            'cesion',
        )
        return cesion.replace('<?xml version="1.0" encoding="ISO-8859-1"?>\n', '')

    def dte_cedido(self):
        xml_cedido = self._dte_cedido()
        dte_cedido = self.firmar(
            xml_cedido,
            self.ID,
            'dte_cedido',
        )
        return dte_cedido
