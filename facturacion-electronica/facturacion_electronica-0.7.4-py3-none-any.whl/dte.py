# -#- coding: utf-8 -#-
from facturacion_electronica.caf import Caf
from facturacion_electronica.emisor import Emisor as Emis
from facturacion_electronica.firma import Firma
from facturacion_electronica import clase_util as util
from lxml import etree
import collections
import base64
import pdf417gen
import logging
_logger = logging.getLogger(__name__)
try:
    from io import BytesIO
except:
    _logger.warning("no se ha cargado io")


class UserError(Exception):
    """Clase perdida"""
    pass


xmlns = "http://www.sii.cl/SiiDte"


class DTE(object):

    def __init__(self, vals):
        self._iniciar()
        util.set_from_keys(self, vals)

    @property
    def Emisor(self):
        if not hasattr(self, '_dte_emisor'):
            self._dte_emisor = Emis()
        return self._dte_emisor

    @Emisor.setter
    def Emisor(self, vals):
        if not hasattr(self, '_dte_emisor'):
            self._dte_emisor = Emis()
        self._dte_emisor.set_from_keys(vals)

    @property
    def caf_files(self):
        return self.caf_file

    @property
    def caf_file(self):
        if not hasattr(self, '_cafs'):
            return []
        return self._cafs

    @caf_file.setter
    def caf_file(self, vals):
        try:
            self._cafs = Caf(vals)
        except Exception as e:
            print("Caf no Soportado o vacío: %s" % str(e))

    @property
    def firma(self):
        if not hasattr(self, '_firma'):
            return False
        return self._firma

    @firma.setter
    def firma(self, val):
        val.verify = self.verify
        self._firma = val

    @property
    def ID(self):
        if not hasattr(self, '_id'):
            return 'Doc1'
        return self._id

    @ID.setter
    def ID(self, val):
        self._id = val

    @property
    def sii_xml_request(self):
        if not hasattr(self, '_sii_xml_request'):
            return False
        return self._sii_xml_request

    @sii_xml_request.setter
    def sii_xml_request(self, val):
        self._sii_xml_request = val

    @property
    def verify(self):
        if not hasattr(self, '_verify'):
            return True
        return self._verify

    @verify.setter
    def verify(self, val):
        self._verify = val

    def _iniciar(self):
        self.respuesta = False
        self.estado_recep_dte = None
        #string con una de las opciones
        '''estado_recep_dte = [
                ('no_revisado','No Revisado'),
                ('0','Conforme'),
                ('1','Error de Schema'),
                ('2','Error de Firma'),
                ('3','RUT Receptor No Corresponde'),
                ('90','Archivo Repetido'),
                ('91','Archivo Ilegible'),
                ('99','Envio Rechazado - Otros')
            ]
        '''

    def crear_DTE(self, doc, tag='DTE'):
        xml = '<' + tag + ' xmlns="http://www.sii.cl/SiiDte" version="1.0">\n'\
            + doc + '\n</' + tag + '>'
        return xml

    def firmar(self, message, uri, type='doc'):
        string = message.replace('<item>', '').replace('</item>', '')\
            .replace('<item/>', '').replace('<itemRefs>', '')\
            .replace('</itemRefs>', '').replace('<itemDscRcgGlobal>', '')\
            .replace('</itemDscRcgGlobal>', '').replace('<cdg_items>', '')\
            .replace('</cdg_items>', '')
        if self.firma.firma:
            return self.firma.firmar(string, uri, type)
        raise UserError('No tiene Firma Válida')

    def get_xml_file(self):
        filename = (self.document_number+'.xml').replace(' ', '')
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=account.invoice\
&field=sii_xml_request&id=%s&filename=%s' % (self.id, filename),
            'target': 'self',
        }

    def get_folio(self):
        return self.Folio

    def pdf417bc(self, ted):
        bc = pdf417gen.encode(
            ted,
            security_level=5,
            columns=13,
            encoding='ISO-8859-1',
        )
        image = pdf417gen.render_image(
            bc,
            padding=10,
            scale=3,
        )
        return image

    def get_related_invoices_data(self):
        """
        List related invoice information to fill CbtesAsoc.
        """
        self.ensure_one()
        rel_invoices = self.search([
            ('number', '=', self.origin),
            ('state', 'not in',
                ['draft', 'proforma', 'proforma2', 'cancel'])])
        return rel_invoices

    def do_dte_send_invoice(self):
        for inv in self:
            if inv.sii_result not in ['', 'NoEnviado', 'Rechazado']:
                raise UserError("El documento %s ya ha sido enviado o está en cola de envío" % inv.Folio)
            inv.responsable_envio = self.env.user.id
            inv.sii_result = 'EnCola'
        self.env['sii.cola_envio'].create({
                                    'doc_ids': self.ids,
                                    'model': 'account.invoice',
                                    'user_id': self.env.user.id,
                                    'tipo_trabajo': 'envio',
                                    })

    def _giros_emisor(self):
        giros_emisor = []
        for turn in self.Emisor.Actecos:
            giros_emisor.extend([{'Acteco': turn}])
        return giros_emisor

    def _emisor(self):
        Emisor = collections.OrderedDict()
        if not self.Emisor.RUTEmisor:
            raise UserError("Debe ingresar el rut del emisor")
        Emisor['RUTEmisor'] = util.format_vat(self.Emisor.RUTEmisor)
        if not self.Emisor.GiroEmis:
            raise UserError("Debe ingresar la glosa descriptiva del giro del emisor")
        if self.es_boleta():
            Emisor['RznSocEmisor'] = self.Emisor.RznSoc
            Emisor['GiroEmis'] = util._acortar_str(self.Emisor.GiroEmis, 80)
        else:
            Emisor['RznSoc'] = self.Emisor.RznSoc
            Emisor['GiroEmis'] = util._acortar_str(self.Emisor.GiroEmis, 80)
            Emisor['Telefono'] = self.Emisor.Telefono
            Emisor['CorreoEmisor'] = self.Emisor.CorreoEmisor
            Emisor['item'] = self._giros_emisor()
        if self.Emisor.CdgSIISucur:
            Emisor['Sucursal'] = self.Emisor.Sucursal
            Emisor['CdgSIISucur'] = self.Emisor.CdgSIISucur
        Emisor['DirOrigen'] = self.Emisor.DirOrigen
        Emisor['CmnaOrigen'] = self.Emisor.CmnaOrigen
        Emisor['CiudadOrigen'] = self.Emisor.CiudadOrigen
        return Emisor

    def set_barcode(self, xml):
        ted = False
        folio = self.Folio
        timbre = """<TED><DD><RE>99999999-9</RE><TD>11</TD><F>1</F>\
<FE>2000-01-01</FE><RR>99999999-9</RR><RSR>\
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX</RSR><MNT>10000</MNT><IT1>IIIIIII\
</IT1></DD></TED>"""
        parser = etree.XMLParser(remove_blank_text=True)
        result = etree.fromstring(timbre, parser=parser)
        xml.append(result)
        result.find('DD/RE').text = self.Emisor.RUTEmisor
        result.find('DD/TD').text = str(self.TipoDTE)
        result.find('DD/F').text = str(folio)
        if not self.FechaEmis:
            raise UserError("Problema con la fecha %s" % self.FechaEmis)
        result.find('DD/FE').text = self.FechaEmis
        if not self._receptor.RUTRecep:
            raise UserError("Completar RUT del Receptor")
        result.find('DD/RR').text = self._receptor.RUTRecep
        result.find('DD/RSR').text = util._acortar_str(
                    self._receptor.RznSocRecep, 40)
        result.find('DD/MNT').text = str(self.MntTotal)
        if self.no_product:
            result.find('DD/MNT').text = '0'
        for line in self._lineas_detalle:
            if line.NroLinDet == 1:
                result.find('DD/IT1').text = util._acortar_str(line.NmbItem, 40)
                break
        resultcaf = self.caf_files.get_caf_file(folio, self.TipoDTE)
        result.find('DD').append(resultcaf.find('CAF'))
        timestamp = util.time_stamp()
        etree.SubElement(result.find('DD'), 'TSTED').text = timestamp
        keypriv = resultcaf.find('RSASK').text.replace('\t', '')
        ddxml = etree.tostring(result.find('DD'), encoding="ISO-8859-1", xml_declaration=False).replace(b'\n', b'')
        firma_caf = Firma({
                    'priv_key': keypriv,
                    'init_signature': False,
                    'rut_firmante': '60803000-K',
                    })
        frmt = firma_caf.generar_firma(ddxml)
        result.set("version", "1.0")
        ted_xml = etree.SubElement(result, 'FRMT')
        ted_xml.set("algoritmo", "SHA1withRSA")
        ted_xml.text = frmt
        ted = etree.tostring(result, encoding="ISO-8859-1", xml_declaration=False).replace(b'\n', b'')
        self.sii_barcode = ted
        image = False
        if ted:
            barcodefile = BytesIO()
            image = self.pdf417bc(ted)
            image.save(barcodefile, 'PNG')
            data = barcodefile.getvalue()
            self.sii_barcode_img = base64.b64encode(data)
        ted_xml = etree.SubElement(xml, 'TmstFirma')
        ted_xml.text = timestamp

    def _dte(self):
        dte = collections.OrderedDict()
        dte['Encabezado'] = self.Encabezado
        if not self._receptor.RUTRecep and not self.es_boleta():
            raise UserError("Debe Ingresar RUT Receptor")
        dte['Encabezado']['Emisor'] = self._emisor()
        if not self.Detalle and self.TipoDTE not in [56, 61]:
            raise UserError("El documento debe llevar una línea, doc: %s\
folio: %s" % (
                                            self.TipoDTE,
                                            self.Folio,
                                        ))
        if not self._resumen and self.TipoDTE in [56, 61] \
                and not self.Referencia:
            raise UserError("Error en %s folio %s, Los documentos de tipo Nota,\
 deben incluir una referencia por obligación" % (self.TipoDTE, self.Folio))
        dte['item'] = self.Detalle
        if self.DscRcgGlobal:
            dte['itemDscRcgGlobal'] = self.DscRcgGlobal
        if self.Referencia:
            dte['itemRefs'] = self.Referencia
        return dte

    def _dte_to_xml(self, dte, tpo_dte="Documento"):
        #ted = dte[tpo_dte + ' ID']['TEDd']
        #dte[(tpo_dte + ' ID')]['TEDd'] = ''
        xml = util.create_xml(dte)
        return xml

    def _tag_dte(self):
        tpo_dte = "Documento"
        if self.TipoDTE == 43:
            tpo_dte = 'Liquidacion'
        return tpo_dte

    def timbrar(self):
        if self.sii_xml_request:
            return
        folio = self.Folio
        tpo_dte = self._tag_dte()
        dte = collections.OrderedDict()
        doc_id_number = "F{}T{}".format(folio, self.TipoDTE)
        #doc_id = '<' + tpo_dte + ' ID="{}">'.format(doc_id_number)
        dte[tpo_dte] = self._dte()
        xml = self._dte_to_xml(dte, tpo_dte)
        if self.caf_files:
            self.set_barcode(xml)
        #xml.set('xmlns', xmlns)
        xml.set('ID', doc_id_number)
        xml_pret = etree.tostring(
                xml,
                pretty_print=True, encoding="ISO-8859-1", xml_declaration=False).decode('ISO-8859-1')
        dte_xml = self.crear_DTE(xml_pret)
        type = 'doc'
        if self.es_boleta():
            type = 'bol'
        einvoice = self.firmar(dte_xml, doc_id_number, type)
        self.sii_xml_request = einvoice

    def format_rut(self, RUTEmisor=None):
        rut = RUTEmisor.replace('-', '')
        if int(rut[:-1]) < 10000000:
            rut = '0' + str(int(rut))
        rut = 'CL'+rut
        return rut
