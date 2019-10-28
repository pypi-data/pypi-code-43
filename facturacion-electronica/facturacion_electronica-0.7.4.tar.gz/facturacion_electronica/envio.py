# -#- coding: utf-8 -#-
#from facturacion_electronica.cesion import Cesion as AEC
from facturacion_electronica.conexion import Conexion
from facturacion_electronica.consumo_folios import ConsumoFolios as CF
from facturacion_electronica.documento import Documento as Doc
from facturacion_electronica.dte import DTE as CDTE
from facturacion_electronica.emisor import Emisor as Emis
from facturacion_electronica.respuesta import Respuesta
from facturacion_electronica.firma import Firma
from facturacion_electronica.libro import Libro as Lib
from facturacion_electronica import clase_util as util
from facturacion_electronica.clase_util import UserError
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class Envio(object):

    def __init__(self, vals, resumen=False):
        self._iniciar()
        util.set_from_keys(self, vals)
        self.conexion = self.test
        self._resumen = resumen

    @property
    def Cesion(self):
        if not hasattr(self, '_cesion'):
            return False
        return self._cesion

    @Cesion.setter
    def Cesion(self, vals):
        self._cesion = AEC(vals)

    @property
    def conexion(self):
        if not hasattr(self, '_conexion'):
            return False
        return self._conexion

    @conexion.setter
    def conexion(self, val):
        if val:
            self._conexion = False
            return
        self._conexion = Conexion(self.Emisor, self.firma)

    @property
    def ConsumoFolios(self):
        if not hasattr(self, '_consumo_folios'):
            return []
        return self._consumo_folios

    @ConsumoFolios.setter
    def ConsumoFolios(self, vals):
        _cfs = []
        for cf in vals:
            _cfs.append(CF(cf))
        self._consumo_folios = _cfs

    @property
    def Documento(self):
        if not hasattr(self, '_documentos'):
            return []
        return self._documentos

    @Documento.setter
    def Documento(self, docs):
        _documentos = []
        CDTE._dte_emsior = self.Emisor
        CDTE._firma = self.firma
        for vals in docs:
            if vals.get('TipoDTE'):
                TipoDTE = vals['TipoDTE']
            if TipoDTE in [39, 41]:
                self.es_boleta = True
            caf_file = vals.get('caf_file', [])
            for docData in vals["documentos"]:
                docu = Doc(
                            docData,
                            resumen=False
                        )
                docu.verify = self.verify
                docu.test = self.test
                if caf_file:
                    docu.caf_file = caf_file
                docu.TipoDTE = TipoDTE
                _documentos.append(docu)
        self._documentos = sorted(_documentos, key=lambda t: t.NroDTE)

    @property
    def DTE(self):
        CDTE._dte_emisor = self.Emisor
        CDTE._firma = self.firma
        return CDTE

    @property
    def Emisor(self):
        if not hasattr(self, '_emisor'):
            self._emisor = Emis()
        return self._emisor

    @Emisor.setter
    def Emisor(self, vals):
        if not hasattr(self, '_emisor'):
            self._emisor = Emis()
        self._emisor.set_from_keys(vals)

    @property
    def errores(self):
        if not hasattr(self, '_errores'):
            return []
        return self._errores

    @errores.setter
    def errores(self, val):
        if not hasattr(self, '_errores'):
            self._errores = [val]
        else:
            self._errores.append(val)

    @property
    def es_boleta(self):
        if not hasattr(self, '_es_boleta'):
            return False
        return self._es_boleta

    @es_boleta.setter
    def es_boleta(self, val):
        self._es_boleta = val

    @property
    def filename(self):
        if not hasattr(self, '_filename'):
            return ''
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = val

    @property
    def firma(self):
        return self.firma_electronica

    @property
    def firma_electronica(self):
        if not hasattr(self, '_firma_electronica'):
            return False
        return self._firma_electronica

    @firma_electronica.setter
    def firma_electronica(self, vals):
        if vals:
            self._firma_electronica = Firma(vals)
        else:
            print("firma no soportada")
            self._firma_electronica = False

    @property
    def Libro(self):
        if not hasattr(self, '_libro'):
            return False
        return self._libro

    @Libro.setter
    def Libro(self, vals):
        CDTE._dte_emisor = self.Emisor
        self._libro = Lib(vals)

    @property
    def Recepciones(self):
        if not hasattr(self, '_recepciones'):
            return []
        return self._recepciones

    @Recepciones.setter
    def Recepciones(self, vals):

        def recursive_xml(el):
            if el.text and bool(el.text.strip()):
                return el.text
            res = {}
            for e in el:
                res[el.tag] = recursive_xml(e)
            return res
        Respuesta._dte_emisor = self._emisor
        _recepciones = []
        for recep in vals:
            respuesta = Respuesta(recep)
            envio = respuesta.xml_envio
            respuesta.Emisor = {
                'RUTEmisor': envio.find('SetDTE/Caratula/RutEmisor').text,
            }
            respuesta.Receptor = {
                'RUTRecep': envio.find('SetDTE/Caratula/RutReceptor').text,
            }
            for dte in envio.findall('SetDTE/DTE'):
                res = recursive_xml(dte)
                respuesta.DTEs = res
            _recepciones.append(respuesta)
        self._recepciones = _recepciones

    @property
    def RecepcionMer(self):
        if not hasattr(self, '_recep_mer'):
            return False
        return self._recep_mer

    @RecepcionMer.setter
    def RecepcionMer(self, vals):
        Respuesta.firma = self.firma
        Respuesta._dte_emisor = self._emisor
        self._recep_mer = Respuesta(vals)

    @property
    def RutReceptor(self):
        if not hasattr(self, '_rut_receptor'):
            return '60803000-K'
        return self._rut_receptor

    @RutReceptor.setter
    def RutReceptor(self, val):
        self._rut_receptor = val

    @property
    def ValidacionCom(self):
        if not hasattr(self, '_validacion_com'):
            return False
        return self._validacion_com

    @ValidacionCom.setter
    def ValidacionCom(self, vals):
        Respuesta.firma = self.firma
        Respuesta._dte_emisor = self._emisor
        self._validacion_com = Respuesta(vals)

    @property
    def test(self):
        if not hasattr(self, '_test'):
            return False
        return self._test

    @test.setter
    def test(self, val):
        self._test = val

    @property
    def verify(self):
        if not hasattr(self, '_verify'):
            return True
        return self._verify

    @verify.setter
    def verify(self, val):
        self._verify = val

    def _iniciar(self):
        self._resumen = False

    def caratula_aec(self):
        dte_cedido = self.Cesion.dte_cedido()
        doc_cedido = self.Cesion.doc_cedido()
        xml = '''<DocumentoAEC ID={0}>
    <Caratula version="1.0">
    <RutCedente>{1}</RutCedente>
    <RutCesionario>{2}</RutCesionario>
    <NmbContacto>{3}</NmbContacto>
    <FonoContacto>{4}</FonoContacto>
    <MailContacto>{5}</MailContacto>
    <TmstFirmaEnvio>{6}</TmstFirmaEnvio>
</Caratula>
    <Cesiones>
        {7}
    </Cesiones>
</DocumentoAEC>
'''.format(
            self.Cesion.ID,
            self.format_vat(self.company_id.vat),
            self.format_vat(self.cesionario_id.commercial_partner_id.vat),
            self.env.user.name,
            self.env.user.phone or self.company_id.phone,
            self.env.user.email or self.company_id.email,
            self.time_stamp(),
            (dte_cedido + '\n' + doc_cedido),
        )
        return xml

    def caratula_consumo_folios(self, cf, IdEnvio='SetDoc'):
        if cf.Correlativo != 0:
            Correlativo = "<Correlativo>"\
                + str(cf.Correlativo) + "</Correlativo>"
        else:
            Correlativo = ''
        xml = '''<DocumentoConsumoFolios ID="{10}">
<Caratula  version="1.0" >
<RutEmisor>{0}</RutEmisor>
<RutEnvia>{1}</RutEnvia>
<FchResol>{2}</FchResol>
<NroResol>{3}</NroResol>
    <FchInicio>{4}</FchInicio>
<FchFinal>{5}</FchFinal>{6}
<SecEnvio>{7}</SecEnvio>
<TmstFirmaEnv>{8}</TmstFirmaEnv>
</Caratula>
{9}
</DocumentoConsumoFolios>
'''.format(self.Emisor.RUTEmisor,
           self.firma_electronica.rut_firmante,
           self.Emisor.FchResol,
           self.Emisor.NroResol,
           cf.FchInicio,
           cf.FchFinal,
           Correlativo,
           str(cf.SecEnvio),
           util.time_stamp(),
           cf.sii_xml_request,
           IdEnvio)
        return xml

    def caratula_dte(self, EnvioDTE, SubTotDTE):
        xml = '''<SetDTE ID="SetDoc">
<Caratula version="1.0">
<RutEmisor>{0}</RutEmisor>
<RutEnvia>{1}</RutEnvia>
<RutReceptor>{2}</RutReceptor>
<FchResol>{3}</FchResol>
<NroResol>{4}</NroResol>
<TmstFirmaEnv>{5}</TmstFirmaEnv>
{6}</Caratula>{7}
</SetDTE>
'''.format(self.Emisor.RUTEmisor,
           self.firma_electronica.rut_firmante\
            if self.firma_electronica else '66666666-6',
           self.RutReceptor,
           self.Emisor.FchResol,
           self.Emisor.NroResol,
           util.time_stamp(),
           SubTotDTE,
           EnvioDTE)
        return xml

    def caratula_libro(self):
        if self.Libro.TipoOperacion == 'BOLETA' and\
                self.Libro.TipoLibro != 'ESPECIAL':
            raise UserError("Boletas debe ser solamente Tipo Operación ESPECIAL")
        if self.Libro.TipoLibro in ['ESPECIAL'] or\
                self.Libro.TipoOperacion in ['BOLETA']:
            FolioNotificacion = '<FolioNotificacion>{0}</FolioNotificacion>'\
                .format(self.Libro.FolioNotificacion)
        else:
            FolioNotificacion = ''
        if self.Libro.TipoOperacion in ['BOLETA', 'GUIA']:
            TipoOperacion = ''
        else:
            TipoOperacion = '<TipoOperacion>' + self.Libro.TipoOperacion\
                + '</TipoOperacion>'
        CodigoRectificacion = ''
        if self.Libro.TipoLibro == 'RECTIFICA':
            CodigoRectificacion = '\n<CodAutRec>' +\
                self.Libro.CodigoRectificacion + '</CodAutRec>'
        xml = '''<EnvioLibro ID="{10}">
<Caratula>
<RutEmisorLibro>{0}</RutEmisorLibro>

<RutEnvia>{1}</RutEnvia>
<PeriodoTributario>{2}</PeriodoTributario>
<FchResol>{3}</FchResol>
<NroResol>{4}</NroResol>{5}
<TipoLibro>{6}</TipoLibro>
<TipoEnvio>{7}</TipoEnvio>
{8}{11}
</Caratula>
{9}
</EnvioLibro>
'''.format(self.Emisor.RUTEmisor,
           self.firma_electronica.rut_firmante\
            if self.firma_electronica else '66666666-6',
           self.Libro.PeriodoTributario,
           self.Emisor.FchResol,
           self.Emisor.NroResol,
           TipoOperacion,
           self.Libro.TipoLibro,
           self.Libro.TipoEnvio,
           FolioNotificacion,
           self.Libro.sii_xml_request,
           self.doc_id,
           CodigoRectificacion,
           )
        return xml

    def envio_aec(self):
        doc_aec = self.caratula_aec()
        xml = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<AEC xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte AEC_v10.xsd" \
version="1.0">
    {}
</AEC>'''.format(doc_aec)
        self.sii_xml_request = xml

    def envio_dte(self, doc):
        xml = '''<EnvioDTE xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte EnvioDTE_v10.xsd" \
version="1.0">
{}
</EnvioDTE>'''.format(doc)
        self.sii_xml_request = xml

    def envio_boleta(self, doc):
        xml = '''<EnvioBOLETA xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte EnvioBOLETA_v11.xsd" \
version="1.0">
{}
</EnvioBOLETA>'''.format(doc)
        return xml

    def envio_libro_cv(self, simplificado=False):
        doc = self.caratula_libro()
        simp = 'http://www.sii.cl/SiiDte LibroCV_v10.xsd'
        if simplificado:
            simp = 'http://www.sii.cl/SiiDte LibroCVS_v10.xsd'
        xml = '''<LibroCompraVenta xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</LibroCompraVenta>'''.format(simp, doc)
        return xml

    def envio_libro_boleta(self):
        doc = self.caratula_libro()
        xsd = 'http://www.sii.cl/SiiDte LibroBOLETA_v10.xsd'
        xml = '''<LibroBoleta xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</LibroBoleta>'''.format(xsd, doc)
        return xml

    def envio_consumo_folios(self, doc):
        xsd = 'http://www.sii.cl/SiiDte ConsumoFolio_v10.xsd'
        xml = '''<ConsumoFolios xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</ConsumoFolios>'''.format(xsd, doc)
        return xml

    def envio_libro_guia(self):
        doc = self.caratula_libro()
        xsd = 'http://www.sii.cl/SiiDte LibroGuia_v10.xsd'
        xml = '''<LibroGuia xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="{0}" \
version="1.0">
{1}</LibroGuia>'''.format(xsd, doc)
        return xml

    def envio_recep(self):
        caratula = self.RecepcionMer.Caratula
        recibos = self.RecepcionMer.Recibos
        xml = '''<EnvioRecibos xmlns='http://www.sii.cl/SiiDte' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://www.sii.cl/SiiDte EnvioRecibos_v10.xsd' version="1.0">
    <SetRecibos ID="SetDteRecibidos">
        {0}
        {1}
    </SetRecibos>
</EnvioRecibos>'''.format(caratula, recibos)
        self.sii_xml_request = xml

    def RespuestaDTE(self, caratula, resultados):
        resp = '''<RespuestaDTE version="1.0" xmlns="http://www.sii.cl/SiiDte" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sii.cl/SiiDte RespuestaEnvioDTE_v10.xsd" >
    <Resultado ID="Odoo_resp">
            {0}
            {1}
    </Resultado>
</RespuestaDTE>'''.format(caratula, resultados)
        self.sii_xml_request = resp

    def Recibo(self, r):
        doc = '''<Recibo version="1.0" xmlns="http://www.sii.cl/SiiDte" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sii.cl/SiiDte Recibos_v10.xsd" >
    <DocumentoRecibo ID="{0}" >
        {1}
    </DocumentoRecibo>
</Recibo>
        '''.format(
            r.ID,
            self.RecepcionMer.recibo(r)
        )
        self.sii_xml_request = doc

    def firmar(self, uri, type='env'):
        result = b''
        if self.firma_electronica.firma:
            result = self.firma_electronica.firmar(
                            self.sii_xml_request, uri, type)
        self.sii_xml_request = result

    def generate_xml_send(self):
        tots_dte = {}
        documentos = ''
        for dte in self.Documento:
            try:
                dte.timbrar()
                tots_dte.setdefault(dte.TipoDTE, {'total': 0, 'folios': []})
                tots_dte[dte.TipoDTE]['total'] += 1
                tots_dte[dte.TipoDTE]['folios'].append(dte.Folio)
                documentos += '\n' + dte.sii_xml_request
            except Exception as e:
                err = {
                        'FechaEmis': dte.FechaEmis,
                        'Folio': dte.Folio,
                        'TipoDTE': dte.TipoDTE,
                        'error': str(e),
                    }
                print(err)
                self.errores = err
        SubTotDTE = ''
        for key, value in tots_dte.items():
            SubTotDTE += '<SubTotDTE>\n<TpoDTE>' + str(key)\
                + '</TpoDTE>\n<NroDTE>'+str(value['total'])+'</NroDTE>\n</SubTotDTE>\n'
            self.filename += 'T%sF' % (key)
            for f in value['folios']:
                self.filename += '%s-' % (f)
        self.filename = self.filename[:-1] + ".xml"
        # firma del sobre
        dtes = self.caratula_dte(documentos, SubTotDTE)
        env = 'env'
        if self.es_boleta:
            self.sii_xml_request = self.envio_boleta(dtes)
            env = 'env_boleta'
        else:
            self.envio_dte(dtes)
        self.firmar(
            'SetDoc',
            env)

    def do_dte_send(self):
        self.generate_xml_send()
        barcodes = []
        for r in self.Documento:
            barcodes.append({
                    'Folio': r.Folio,
                    'TpoDTE': r.TipoDTE,
                    'sii_barcode_img': r.sii_barcode_img
                })
        result = {
            'sii_result': 'draft',
            }
        if not self.test and self.conexion:
            result = self.conexion.send_xml_file(
                            self.sii_xml_request,
                            self.filename
                        )
        result.update({
                'sii_xml_request': '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request,
                'sii_send_filename': self.filename,
                'barcodes': barcodes,
                'errores': self.errores,
                })
        return result

    def do_libro_send(self):
        if not self.Libro.validar():
            return []
        self.doc_id = self.Libro.TipoOperacion + '_' + \
            self.Libro.PeriodoTributario
        env = 'libro'
        if self.Libro.TipoOperacion in ['BOLETA']:
                xml = self.envio_libro_boleta()
                env = 'libro_boleta'
        elif self.Libro.TipoOperacion == 'GUIA':
            xml = self.envio_libro_guia()
            env = 'libro_guia'
        else:
            xml = self.envio_libro_cv()
        self.sii_xml_request = xml
        self.firmar(
            self.doc_id,
            env)
        result = {'sii_result': 'draft'}
        self.sii_xml_request = self.sii_xml_request
        if not self.test:
            result = self.conexion.send_xml_file(
                            self.sii_xml_request,
                            self.doc_id + '.xml'
                        )
        result.update({
            'sii_xml_request': '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request,
            'sii_send_filename': self.filename + ".xml",
            'errores': self.errores,
            })
        return result

    def do_consumo_folios_send(self):
        results = []
        for _cf in self.ConsumoFolios:
            if not _cf.validar():
                continue
            self.filename = 'CF_' + _cf.FchInicio
            cf = self.caratula_consumo_folios(
                _cf
            )
            self.envio_consumo_folios(cf)
            self.firmar(
                'SetDoc',
                type='consu',
            )
            result = {'sii_result': 'draft'}
            sii_xml_request = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request
            if not self.test:
                result = self.conexion.send_xml_file(
                                sii_xml_request,
                                self.filename
                            )
            result.update({
                    'sii_xml_request': sii_xml_request,
                    'sii_send_filename': self.filename + ".xml",
                    })
            results.append(result)
        return results

    def do_receipt_deliver(self):
        resps = []
        CDTE.firma = self.firma_electronica
        for r in self.Recepciones:
            self.RespuestaDTE(r.Caratula, r.RecepcionEnvio)
            self.firmar(
                'Odoo_resp',
                'env_resp',
            )
            resp = {
                'respuesta_xml': '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request,
                'nombre_xml': 'recepcion_envio_%s_%s.xml' %
                (r.xml_nombre, str(r.IdRespuesta)),
                'EstadoRecepEnv': r.EstadoRecepEnv,
                'RecepEnvGlosa': r.RecepEnvGlosa,
            }
            resps.append(resp)
        return resps

    def do_recep_merc(self):
        for r in self.RecepcionMer.DTEs:
            self.Recibo(r)
            self.firmar(
                r.ID,
                'env_recep')
            self.RecepcionMer.Recibos = self.sii_xml_request
        self.envio_recep()
        self.firmar(
                'SetDteRecibidos',
                'env_recep'
            )
        return {
                'respuesta_xml': '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request,
                'nombre_xml': 'recepcion_mercaderias_%s.xml' % str(
                            self.RecepcionMer.DTEs[0].ID)
            }

    def do_validar_com(self):
        self.ValidacionCom.gen_validacion_comercial()
        self.RespuestaDTE(self.ValidacionCom.Caratula,
                          self.ValidacionCom.Resultados)
        self.firmar(
            'Odoo_resp',
            'env_resp'
        )
        return {
            'respuesta_xml': '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request,
            'nombre_xml': 'validacion_comercial_%s.xml' % str(
                            self.ValidacionCom.IdRespuesta),
            'EstadoDTE': self.ValidacionCom.EstadoDTE,
            'EstadoDTEGlosa': self.ValidacionCom.EstadoDTEGlosa,
        }

    def do_envio_cesion(self):
        self.crear_envio_aec()
        self.firmar(
            'Doc1',
            'aec',
        )
        return{
            'respuesta_xml': '<?xml version="1.0" encoding="ISO-8859-1"?>\n'\
                + self.sii_xml_request,
            'nombre_xml': 'cesion.xml'
        }
