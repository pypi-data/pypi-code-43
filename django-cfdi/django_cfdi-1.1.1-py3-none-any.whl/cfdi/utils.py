import sys
import codecs
import re
import datetime
from cfdi import XmlNewObject, Object
from .functions import to_decimal, to_int, to_datetime, to_precision_decimales

def es_producto_combustible(claveprodserv):
    return claveprodserv in ["15101506", "15101505"]

def get_fecha_cfdi(fecha):
    fecha_str = fecha.replace("Z", "").split('.')[0][0:19]
    return to_datetime(
        datetime.datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
    )

def get_xml_value(xml_content, field):
    try:
        return (
            xml_content.split('%s="' % field)[1].split('"')[0].upper().strip()
        )
    except:
        return ""
        
def unescape(string):
    return (
        str(string)
        .replace("&apos;", "'")
        .replace("&quot;", '"')
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )

def get_field(field, value):
    """
    Agrega el campo al XML según el valor de dicho
    campo en la clase CFDI.
    """
    if value == "" or value is None:
        return ""

    return '%s="%s" ' % (field, escape(value))
    
def remover_addenda(xml):
    if "<cfdi:Addenda" in xml:
        return xml.split("<cfdi:Addenda")[0] + "</cfdi:Comprobante>"
    return xml

def get_addenda(tipo_addenda, diccionario):
    import importlib
    addenda = importlib.import_module("%s.addendas.%s.addenda" % (
        __package__, tipo_addenda
    ))
    return addenda.generar_addenda(diccionario)
    

def decode_text(txt, es_cfdi=True):
    """
    Recibe un string lo intenta codificar en utf8 y otros posibles
    encodings, y regresa el texto como unicode.
    """

    if es_cfdi:
        """ 
            SI EL TEXTO ES UN CFDI XML Y EMPIEZA CON UN '?' 
            SE QUITA EL SIGNO PARA QUE SEA UN XML VÁLIDO
        """

        if isinstance(txt, bytes):
            signo = b"?"
        else:
            signo = "?"

        if txt.startswith(signo):
            txt = txt[1:]

    if not isinstance(txt, bytes):
        return txt

    e = None
    for encoding in ["utf-8", "cp1252", ]:
        try:
            return txt.decode(encoding)
        except UnicodeDecodeError as exception:
            e = exception
            continue
        else:
            break
    else:
        raise e


def get_xml_object(xml_text):

    """
    El tipo de cambio de la moneda USD lo toma de la bsae de datos central,
    de acuerdo al tipo de cambio del DOF.
    """
    TIPOS_REGIMEN = (
        # (1, 'Asimilados a salarios (DESCONTINUADO)'),
        (2, "Sueldos y salarios"),
        (3, "Jubilados"),
        (4, "Pensionados"),
        (
            5,
            (
                "Asimilados a salarios, Miembros de las Sociedades "
                "Cooperativas de Producción."
            ),
        ),
        (
            6,
            (
                "Asimilados a salarios, Integrantes de Sociedades "
                "y Asociaciones Civiles"
            ),
        ),
        (
            7,
            (
                "Asimilados a salarios, Miembros de consejos directivos, "
                "de vigilancia, consultivos, honorarios a administradores, "
                "comisarios y gerentes generales."
            ),
        ),
        (8, "Asimilados a salarios, Actividad empresarial (comisionistas)"),
        (9, "Asimilados a salarios, Honorarios asimilados a salarios"),
        (10, "Asimilados a salarios, Ingresos acciones o títulos valor"),
    )

    RIESGO_PUESTOS = (
        (0, "------"),
        (1, "Clase I"),
        (2, "Clase II"),
        (3, "Clase III"),
        (4, "Clase IV"),
        (5, "Clase V"),
    )

    xml_text = xml_text.strip()

    if not xml_text:
        return None

    xml_text = decode_text(xml_text)
    cond1 = xml_text.encode("utf-8").startswith(codecs.BOM_UTF8 + b"<")
    cond2 = xml_text.encode("utf-8").startswith(b"<")

    if not cond1 and not cond2:
        return None

    xml_text = remover_addenda(xml_text)
    soup = XmlNewObject(texto=xml_text)
    xml = Object()
    xml.complemento = None
    version = 3
    reg_entero = re.compile(r"[^\d]+")
    o = soup.find("comprobante")

    if o.get("version", "") == "3.3":
        xml.es_v33 = True
        xml.formadepago = o.get("metodopago", "")
        xml.metododepago = o.get("formapago", "")
    else:
        xml.formadepago = o.get("formadepago", "")
        xml.metododepago = o.get("metododepago", "")
        xml.es_v33 = False
        if o.find("regimenfiscal"):
            xml.regimen = o.find("regimenfiscal").get("regimen")

    xml.forma_pago_at = 1 if xml.formadepago == "PPD" else 0
    xml.version = version
    xml.total = o.get("total", "")
    xml.sello = o.get("sello", "")
    xml.noaprobacion = o.get("noaprobacion", "")
    xml.anoaprobacion = o.get("anoaprobacion", "")
    xml.nocertificado = o.get("nocertificado", "")
    xml.folio = reg_entero.sub("", o.get("folio", "")[-9:])
    xml.serie = o.get("serie", "")
    xml.fecha_str = o.get("fecha", "")
    xml.fecha_dt = get_fecha_cfdi(xml.fecha_str)

    # __PENDIENTE__ eliminar para evitar confusiones
    # con la fecha en formato texto o datetime
    xml.fecha = xml.fecha_str

    xml.subtotal = o.get("subtotal", "")
    xml.descuento = o.get("descuento", "")

    xml.numctapago = o.get("numctapago", "")
    xml.condicionesdepago = o.get("condicionesdepago", "")
    xml.moneda = o.get("moneda", "")
    xml.tipocambio = o.get("tipocambio", "1")

    xml.tipodecomprobante = o.get("tipodecomprobante", "")
    xml.lugarexpedicion = o.get("lugarexpedicion", "")

    ######## EMISOR ########
    xml.emisor = Object()
    xml.emisor.rfc = o.find("emisor").get("rfc").strip()
    xml.emisor.nombre = unescape(o.find("emisor").get("nombre"))
    if o.get("version", "") == "3.3":
        xml.regimen = o.find("emisor").get("regimenfiscal", "")

    xml.emisor.domiciliofiscal = Object()
    xml.emisor.domiciliofiscal.calle = (
        o.find("emisor").find("domiciliofiscal").get("calle", "")[:500]
    )
    xml.emisor.domiciliofiscal.noexterior = (
        o.find("emisor").find("domiciliofiscal").get("noexterior", "")[:100]
    )
    xml.emisor.domiciliofiscal.nointerior = (
        o.find("emisor").find("domiciliofiscal").get("nointerior", "")[:100]
    )
    xml.emisor.domiciliofiscal.colonia = (
        o.find("emisor").find("domiciliofiscal").get("colonia", "")[:100]
    )
    xml.emisor.domiciliofiscal.municipio = (
        o.find("emisor").find("domiciliofiscal").get("municipio", "")[:255]
    )
    xml.emisor.domiciliofiscal.localidad = (
        o.find("emisor").find("domiciliofiscal").get("localidad", "")[:255]
    )
    xml.emisor.domiciliofiscal.estado = (
        o.find("emisor").find("domiciliofiscal").get("estado", "")[:255]
    )
    xml.emisor.domiciliofiscal.pais = (
        o.find("emisor").find("domiciliofiscal").get("pais", "")[:100]
    )
    xml.emisor.domiciliofiscal.codigopostal = (
        o.find("emisor").find("domiciliofiscal").get("codigopostal", "")[:6]
    )
    ########

    ######## RECEPTOR ########
    xml.receptor = Object()
    xml.receptor.rfc = o.find("receptor").get("rfc").strip()
    xml.receptor.nombre = unescape(o.find("receptor").get("nombre"))
    xml.receptor.regimen = o.find("receptor").get("regimen") or o.find(
        "receptor"
    ).get("regimenfiscal")
    xml.receptor.registro_patronal = o.find("receptor").get("registropatronal")
    xml.receptor.usocfdi = o.find("receptor").get("usocfdi")

    xml.receptor.domicilio = Object()
    xml.receptor.domicilio.calle = (
        o.find("receptor").find("domicilio").get("calle", "")
    )
    xml.receptor.domicilio.noexterior = (
        o.find("receptor").find("domicilio").get("noexterior", "")
    )
    xml.receptor.domicilio.nointerior = (
        o.find("receptor").find("domicilio").get("nointerior", "")
    )
    xml.receptor.domicilio.colonia = (
        o.find("receptor").find("domicilio").get("colonia", "")
    )
    xml.receptor.domicilio.municipio = (
        o.find("receptor").find("domicilio").get("municipio", "")
    )
    xml.receptor.domicilio.localidad = (
        o.find("receptor").find("domicilio").get("localidad", "")
    )
    xml.receptor.domicilio.estado = (
        o.find("receptor").find("domicilio").get("estado", "")
    )
    xml.receptor.domicilio.pais = (
        o.find("receptor").find("domicilio").get("pais", "")
    )
    xml.receptor.domicilio.codigopostal = (
        o.find("receptor").find("domicilio").get("codigopostal", "")[0:5]
    )
    direccion_completa = xml.receptor.domicilio.calle

    if xml.receptor.domicilio.noexterior:
        direccion_completa = "%s #%s" % (
            direccion_completa,
            xml.receptor.domicilio.noexterior,
        )

    if xml.receptor.domicilio.colonia:
        direccion_completa = "%s Col: %s" % (
            direccion_completa,
            xml.receptor.domicilio.colonia,
        )

    if xml.receptor.domicilio.codigopostal:
        direccion_completa = "%s CP: %s" % (
            direccion_completa,
            xml.receptor.domicilio.codigopostal,
        )

    direccion_completa = "%s %s %s" % (
        direccion_completa,
        xml.receptor.domicilio.municipio,
        xml.receptor.domicilio.estado,
    )

    xml.receptor.domicilio.completa = direccion_completa
    ########
    xml.iva = 0
    xml.importe_tasa_cero = 0
    xml.importe_tasa_general = 0
    xml.importe_tasa_frontera = 0
    xml.importe_exento = 0
    xml.total_tasa_cero = 0
    xml.total_tasa_general = 0
    xml.total_tasa_frontera = 0
    xml.total_exento = 0
    xml.tasa_cero = False
    xml.ieps = 0
    xml.retencion_isr = 0
    xml.retencion_iva = 0
    total_traslados = 0
    total_retenciones = 0

    conceptos = o.find("conceptos").find_list("concepto")
    xml.conceptos = []

    importe_tasa_frontera = 0
    total_impuestos_tasa_fronetra = 0
    importe_tasa_general = 0
    total_impuestos_tasa_general = 0

    xml.importe_iva_frontera = 0
    xml.importe_iva_tasa_general = 0

    for c in conceptos:
        tasa_iva_concepto = ""
        tasa_ieps_concepto = ""
        total_iva = 0
        total_ieps = 0
        base_iva = ""
        total_base_iva_concepto = 0
        base_ieps = ""
        tipo_factor_ieps = "tasa"
        cuota_ieps = None
        descuento = to_decimal(c.get("descuento"))
        total_traslado_concepto = 0
        importe_tasa_frontera_concepto = 0
        importe_tasa_general_concepto = 0
        cantidad = to_decimal(c.get("cantidad"))
        es_combustible = False
        if xml.es_v33:
            importe_concepto = to_decimal(c.get("importe"))
            claveprodserv = c.get("claveprodserv", "")
            for tras in c.find_list("traslado"):
                tasa_iva = ""
                tasa_ieps = ""
                importe_ieps = 0
                cuota_ieps = None
                importe_traspaso = to_decimal(tras.get("importe"))
                base_traslado = to_decimal(tras.get("base"))
                if to_decimal(tras.get("base")):
                    if tras.get("impuesto").upper() == "002":
                        tasa_iva = tras.get("tasaocuota")
                        tasa_iva_concepto = tasa_iva
                        total_iva += importe_traspaso
                        if tras.get("tipofactor", "").lower() == "exento":
                            tasa_iva = "exento"

                    elif tras.get("impuesto").upper() == "003":
                        tasa_ieps = tras.get("tasaocuota")
                        tasa_ieps_concepto = tasa_ieps
                        total_ieps += to_decimal(tras.get("importe"))
                        importe_ieps = to_decimal(tras.get("importe"))
                        tipo_factor_ieps = tras.get("tipofactor").lower()

                        if tipo_factor_ieps == "cuota":
                            cuota_ieps = tasa_ieps

                    total_traslado_concepto += importe_traspaso

            es_frontera = to_decimal(tasa_iva_concepto) == to_decimal("0.08")
            if es_frontera:
                xml.importe_iva_frontera += total_iva
            else:
                xml.importe_iva_tasa_general += total_iva

            es_combustible = es_producto_combustible(
                claveprodserv
            ) and not to_decimal(total_ieps)

            if es_combustible:
                cuota_ieps = (
                    importe_concepto - descuento - base_traslado
                ) / cantidad

            es_tasa_cero = (
                tasa_iva_concepto
                and not to_decimal(tasa_iva_concepto)
                and tasa_iva_concepto != "exento"
            )
            if tasa_iva_concepto:
                # SI ES COMBUSTIBLE, TOMA TODO EL IMPORTE DEL
                # CONCEPTO PARA EL TOTAL DE TASA GENERAL/FRONTERA
                if es_combustible:
                    importe_tasa = base_traslado
                else:
                    importe_tasa = importe_concepto - descuento

                if to_decimal(tasa_iva_concepto):
                    if es_frontera:
                        importe_tasa_frontera += importe_tasa
                        total_impuestos_tasa_fronetra += (
                            total_traslado_concepto
                        )
                        if not es_combustible:
                            xml.importe_tasa_frontera += importe_tasa
                    else:

                        importe_tasa_general += importe_tasa
                        total_impuestos_tasa_general += total_traslado_concepto
                        if not es_combustible:
                            xml.importe_tasa_general += importe_tasa

                elif es_tasa_cero:
                    xml.importe_tasa_cero += importe_tasa
                    xml.total_tasa_cero += (
                        importe_tasa + total_traslado_concepto
                    )

            for t in c.find_list("retencion"):
                if t.get("impuesto").upper() == "002":
                    xml.retencion_iva += to_decimal(t.get("importe"))
                elif t.get("impuesto").upper() == "001":
                    xml.retencion_isr += to_decimal(t.get("importe"))

            xml.iva += total_iva
            xml.ieps += total_ieps

        else:
            base_iva = to_decimal(c.get("importe"))
            tasa_iva = to_decimal("0.16")

        xml.conceptos.append(
            {
                "cantidad": to_decimal(cantidad),
                "claveprodserv": c.get("claveprodserv"),
                "claveunidad": c.get("claveunidad"),
                "descripcion": unescape(c.get("descripcion")),
                "importe": c.get("importe"),
                "noidentificacion": unescape(
                    c.get("noidentificacion", "").strip()
                )[:100],
                "unidad": (
                    c.get("unidad") or c.get("claveunidad")
                ),  # version 3.3,
                "valorunitario": c.get("valorunitario"),
                "tasa_iva": tasa_iva_concepto,
                "total_iva": total_iva,
                "tasa_ieps": tasa_ieps_concepto,
                "total_ieps": total_ieps,
                "base_iva": base_iva,
                "base_ieps": base_ieps,
                "tipo_factor_ieps": tipo_factor_ieps,
                "descuento": descuento,
                "importe_con_descuento": (
                    to_decimal(c.get("importe")) - to_decimal(descuento)
                ),
                "cuota_ieps": to_precision_decimales(cuota_ieps, 4),
                "es_combustible": es_combustible,
            }
        )

    xml.retencion_iva = to_precision_decimales(xml.retencion_iva, 2)
    xml.retencion_isr = to_precision_decimales(xml.retencion_isr, 2)
    xml.total_tasa_frontera += to_precision_decimales(
        importe_tasa_frontera, 2
    ) + to_precision_decimales(total_impuestos_tasa_fronetra, 2)

    xml.total_tasa_general += to_precision_decimales(
        importe_tasa_general, 2
    ) + to_precision_decimales(total_impuestos_tasa_general, 2)

    if not xml.es_v33:
        for t in o.find("impuestos").find("traslados").find_list("traslado"):
            importe_traslado = to_decimal(t.get("importe"))
            if t.get("impuesto") == "IVA":
                xml.iva += importe_traslado
            elif t.get("impuesto") == "IEPS":
                xml.ieps += importe_traslado

    pago = o.find("pagos", "pago10")
    xml.es_comprobante_pago = False
    if pago.exists:
        xml.es_comprobante_pago = True
        xml.abono_fecha_pago = pago.get("fechapago")
        xml.abono_forma_pago = pago.get("formadepagop")
        xml.abono_moneda = pago.get("monedap")
        xml.abono_monto = pago.get("monto")
        xml.abono_num_operacion = pago.get("numoperacion")

        xml.banco_ordenante = pago.get("nombancoordext")
        xml.cuenta_ordenante = pago.get("ctaordenante")
        xml.rfc_cuenta_ordenante = pago.get("rfcemisorctaord")
        xml.rfc_cuenta_beneficiario = pago.get("rfcemisorctaben")
        xml.cuenta_beneficiario = pago.get("ctabeneficiario")

        xml.pagos = []
        for p in pago.find_list("doctorelacionado", "pago10"):
            xml.pagos.append(
                {
                    "imp_pagado": p.get("imppagado"),
                    "imp_saldo_ant": p.get("impsaldoant"),
                    "imp_saldo_insoluto": p.get("impsaldoinsoluto"),
                    "metodo_pago": p.get("metododepagodr"),
                    "moneda": p.get("monedadr"),
                    "num_parcialidad": p.get("numparcialidad"),
                    "folio": p.get("folio"),
                    "serie": p.get("serie"),
                    "iddocumento": p.get("iddocumento"),
                }
            )

    xml.impuestos = Object()
    xml.impuestos.totalimpuestostrasladados = o.find("impuestos").get_num(
        "totalimpuestostrasladados"
    )

    xml.impuestos.totalImpuestosRetenidos = o.find("impuestos").get_num(
        "totalimpuestosretenidos"
    )
    impuestoslocales = o.find_list("impuestoslocales", "implocal")
    xml.impuestos_locales = []
    xml.total_impestos_locales = 0
    if impuestoslocales:
        for il in impuestoslocales:
            xml.impuestos_locales.append(
                {
                    "nombre": il.get("implocretenido"),
                    "importe": il.get("importe"),
                    "tasa": il.get("tasaderetencion"),
                }
            )

            xml.total_impestos_locales += to_decimal(il.get("importe"))

    if not xml.iva:
        xml.tasa_cero = True

    xml.importe_tasa_general = to_precision_decimales(xml.importe_tasa_general)
    xml.importe_tasa_cero = to_precision_decimales(xml.importe_tasa_cero)
    xml.total_tasa_general = to_precision_decimales(xml.total_tasa_general)
    xml.total_tasa_cero = (
        to_precision_decimales(xml.total_tasa_cero)
        + xml.total_impestos_locales
    )
    xml.total_tasa_frontera = to_precision_decimales(xml.total_tasa_frontera)

    xml.importe_exento = (
        to_decimal(xml.subtotal)
        - to_decimal(xml.descuento)
        - xml.importe_tasa_general
        - xml.importe_tasa_frontera
        - xml.importe_tasa_cero
    )

    xml.total_exento = (
        to_decimal(xml.total)
        - xml.total_tasa_general
        - xml.total_tasa_frontera
        - xml.total_tasa_cero
    )

    if xml.total_tasa_general or xml.total_tasa_frontera:
        """
            SI HAY IMPUESTOS RETENIDOS, SE SUMA AL EXENTO POR QUE 
            SE LE RESTA ARRIBA (TOTAL_TASA_GENERAL O TOTAL_TASA_FRONTERA)
        """
        xml.total_exento += xml.impuestos.totalImpuestosRetenidos

    if version == 3:
        xml.complemento = Object()
        xml.complemento.timbrefiscaldigital = Object()
        complemento = o.find("complemento")

        for version_ecc in ["ecc11", "ecc12"]:

            estado_cuenta_combustible = XmlNewObject(texto=xml_text).find(
                "EstadoDeCuentaCombustible", version_ecc
            )
            conceptos_combustible = []
            for concepto in estado_cuenta_combustible.find_list(
                "ConceptoEstadoDeCuentaCombustible", version_ecc
            ):
                iva = (
                    concepto.find("Traslados", version_ecc)
                    .find_list("Traslado", version_ecc)[0]
                    .get("Importe")
                )
                conceptos_combustible.append(
                    {
                        "fecha": concepto.get("Fecha"),
                        "rfc": concepto.get("Rfc"),
                        "importe": to_decimal(concepto.get("Importe")),
                        "iva": to_decimal(iva),
                    }
                )

        xml.complemento.conceptos_combustible = conceptos_combustible
        xml.complemento.timbrefiscaldigital.uuid = ""
        if complemento.exists:
            tfd = complemento.find("timbrefiscaldigital", "tfd")
            if tfd.exists:
                xml.complemento.timbrefiscaldigital.version = tfd.get(
                    "version"
                )
                xml.complemento.timbrefiscaldigital.uuid = tfd.get("uuid")
                xml.complemento.timbrefiscaldigital.fechatimbrado_str = tfd.get(
                    "fechatimbrado"
                )
                xml.complemento.timbrefiscaldigital.fechatimbrado_dt = get_fecha_cfdi(
                    xml.complemento.timbrefiscaldigital.fechatimbrado_str
                )
                xml.complemento.timbrefiscaldigital.sellocfd = tfd.get(
                    "sellocfd"
                )
                xml.complemento.timbrefiscaldigital.nocertificadosat = tfd.get(
                    "nocertificadosat"
                )
                xml.complemento.timbrefiscaldigital.sellosat = tfd.get(
                    "sellosat"
                )
                xml.complemento.timbrefiscaldigital.rfcprovcertif = tfd.get(
                    "rfcprovcertif", ""
                )

                if xml.complemento.timbrefiscaldigital.uuid:
                    xml.complemento.timbrefiscaldigital.cadenaoriginal = (
                        "||1.0|%s|%s|%s|%s||"
                        % (
                            xml.complemento.timbrefiscaldigital.uuid,
                            xml.complemento.timbrefiscaldigital.fechatimbrado_str,
                            xml.complemento.timbrefiscaldigital.sellocfd,
                            xml.complemento.timbrefiscaldigital.nocertificadosat,
                        )
                    )

                    xml.qrcode = 'https://' + \
                        'verificacfdi.facturaelectronica.sat.gob.mx' + \
                        '/default.aspx?&id=%s&re=%s&rr=%s&tt=%s&fe=%s' % (
                        
                        xml.complemento.timbrefiscaldigital.uuid,
                        xml.emisor.rfc,
                        xml.receptor.rfc,
                        xml.total,
                        xml.sello[-8:],
                    )

                else:
                    xml.complemento.timbrefiscaldigital.cadenaoriginal = ""

            nomina_xml = complemento.find("nomina", "nomina12")
            if not nomina_xml.exists:
                nomina_xml = complemento.find("nomina", "nomina")

            if nomina_xml.exists:
                xml.complemento.nomina = Object()
                nomina_version = nomina_xml.get("version")

                receptor_nomina = nomina_xml.find("receptor")
                xml.complemento.nomina.numero_empleado = receptor_nomina.get(
                    "numempleado", ""
                )
                xml.complemento.nomina.curp = receptor_nomina.get("curp", "")
                xml.complemento.nomina.nss = receptor_nomina.get(
                    "numseguridadsocial", ""
                )
                xml.complemento.nomina.tipo_regimen = to_int(
                    receptor_nomina.get("tiporegimen", "")
                )
                xml.complemento.nomina.get_tipo_regimen_display = dict(
                    TIPOS_REGIMEN
                ).get(string_to_int(xml.complemento.nomina.tipo_regimen), "")
                xml.complemento.nomina.fecha_inicio = nomina_xml.get(
                    "fechainicialpago", ""
                )
                xml.complemento.nomina.fecha_fin = nomina_xml.get(
                    "fechafinalpago", ""
                )
                xml.complemento.nomina.fecha_pago = nomina_xml.get(
                    "fechapago", ""
                )
                xml.complemento.nomina.dias = nomina_xml.get(
                    "numdiaspagados", ""
                )
                xml.complemento.nomina.departamento = receptor_nomina.get(
                    "departamento", ""
                )
                xml.complemento.nomina.puesto = receptor_nomina.get(
                    "puesto", ""
                )
                xml.complemento.nomina.tipo_contrato = receptor_nomina.get(
                    "tipocontrato", ""
                )
                xml.complemento.nomina.tipo_jornada = receptor_nomina.get(
                    "tipojornada", ""
                )
                xml.complemento.nomina.riesgo_puesto = receptor_nomina.get(
                    "riesgopuesto", ""
                )
                xml.complemento.nomina.get_riesgo_puesto_display = (
                    RIESGO_PUESTOS[
                        string_to_int(xml.complemento.nomina.riesgo_puesto)
                    ][1]
                    if to_int(xml.complemento.nomina.riesgo_puesto)
                    else None
                )
                xml.complemento.nomina.sdi = receptor_nomina.get(
                    "salariodiariointegrado", ""
                )
                xml.complemento.nomina.sbc = receptor_nomina.get(
                    "salariobasecotapor", ""
                )
                xml.complemento.nomina.fecha_iniciorel_laboral = receptor_nomina.get(
                    "fechainiciorellaboral", ""
                )
                xml.complemento.nomina.antiguedad = receptor_nomina.get(
                    "Antig\xfcedad", ""
                )
                xml.complemento.nomina.clabe = receptor_nomina.get("clabe", "")
                xml.complemento.nomina.periodicidadpago = receptor_nomina.get(
                    "periodicidadpago", ""
                )
                xml.complemento.nomina.claveentfed = receptor_nomina.get(
                    "claveentfed", ""
                )
                xml.complemento.nomina.registro_patronal = nomina_xml.find(
                    "emisor"
                ).get("registropatronal", "")
                esncf = nomina_xml.find("emisor").get("entidadsncf", {})
                xml.complemento.nomina.origen_recurso = esncf.get(
                    "origenrecurso", ""
                )
                xml.complemento.nomina.monto_recurso_propio = esncf.get(
                    "montorecursopropio", ""
                )
                xml.complemento.nomina.tipo_nomina = nomina_xml.get(
                    "tiponomina", ""
                )

                percepciones = nomina_xml.find("percepciones").find_list(
                    "percepcion"
                )
                xml.complemento.nomina.percepciones = []
                xml.complemento.nomina.total_gravado = 0
                xml.complemento.nomina.total_exento = 0
                xml.complemento.nomina.total_percepciones = 0
                if percepciones:
                    for p in percepciones:
                        xml.complemento.nomina.percepciones.append(
                            {
                                "clave": p.get("clave"),
                                "concepto": p.get("concepto"),
                                "importegravado": p.get("importegravado"),
                                "importeexento": p.get("importeexento"),
                                "tipo": p.get("tipopercepcion"),
                            }
                        )
                        xml.complemento.nomina.total_gravado += to_decimal(
                            p.get("importegravado")
                        )
                        xml.complemento.nomina.total_exento += to_decimal(
                            p.get("importeexento")
                        )
                        xml.complemento.nomina.total_percepciones += to_decimal(
                            p.get("importegravado")
                        ) + to_decimal(
                            p.get("importeexento")
                        )

                otrospagos = nomina_xml.find("otrospagos").find_list(
                    "otropago"
                )
                xml.complemento.nomina.otrospagos = []
                xml.complemento.nomina.total_otrospagos = 0
                if otrospagos:
                    for p in otrospagos:

                        xml.complemento.nomina.subsidio = 0
                        subsidio = p.find("subsidioalempleo")
                        if subsidio.exists:
                            xml.complemento.nomina.subsidio = to_decimal(
                                subsidio.get("subsidiocausado")
                            )

                        xml.complemento.nomina.otrospagos.append(
                            {
                                "clave": p.get("clave"),
                                "concepto": p.get("concepto"),
                                "importe": p.get("importe"),
                                "tipo": p.get("tipootropago"),
                            }
                        )
                        xml.complemento.nomina.total_otrospagos += to_decimal(
                            p.get("importe")
                        )

                deducciones = nomina_xml.find("deducciones").find_list(
                    "deduccion"
                )
                xml.complemento.nomina.deducciones = []
                xml.complemento.nomina.total_deducciones = 0
                if deducciones:
                    for d in deducciones:
                        xml.complemento.nomina.deducciones.append(
                            {
                                "clave": d.get("clave"),
                                "concepto": d.get("concepto"),
                                "importe": d.get("importe"),
                                "tipo": d.get("tipodeduccion"),
                            }
                        )
                        xml.complemento.nomina.total_deducciones += to_decimal(
                            d.get("importe")
                        )

                horasextra = nomina_xml.find("horasextra").find_list(
                    "horaextra"
                )
                xml.complemento.nomina.horasextra = []

                if horasextra:
                    for he in horasextra:
                        xml.complemento.nomina.horasextra.append(he)

                incapacidades = nomina_xml.find("incapacidades").find_list(
                    "incapacidad"
                )
                xml.complemento.nomina.incapacidades = []
                if incapacidades:
                    for i in incapacidades:
                        xml.complemento.nomina.incapacidades.append(i)

                xml.complemento.nomina.total_percibido = to_decimal(xml.total)

            else:
                xml.complemento.nomina = None

            ine = complemento.find("ine", "ine")
            if ine.exists:
                xml.complemento.ine = Object()
                xml.complemento.ine.tipoproceso = ine.get("tipoproceso", "")
                xml.complemento.ine.tipocomite = ine.get("tipocomite", "")
                if ine.find("entidad"):
                    xml.complemento.ine.claveentidad = ine.find("entidad").get(
                        "claveentidad", ""
                    )
                    if ine.find("entidad").find("contabilidad"):
                        xml.complemento.ine.idcontabilidad = (
                            ine.find("entidad")
                            .find("contabilidad")
                            .get("idcontabilidad", "")
                        )

            iedu = complemento.find("insteducativas", "iedu")
            if iedu.exists:
                xml.complemento.iedu = Object()
                xml.complemento.version = iedu.get("version")
                xml.complemento.autrvoe = iedu.get("autrvoe")
                xml.complemento.nombre_alumno = iedu.get("nombrealumno")
                xml.complemento.curp = iedu.get("curp")
                xml.complemento.nivel_educativo = iedu.get("niveleducativo")
                xml.complemento.rfc_pago = iedu.get("rfcpago")

    xml.es_dolares = False
    xml.es_euros = False
    xml.importe = (
        to_decimal(xml.total)
        - to_decimal(xml.iva)
        - to_decimal(xml.ieps)
        + xml.impuestos.totalImpuestosRetenidos
    )

    xml.total = to_decimal(xml.total)
    xml.subtotal = to_decimal(xml.subtotal)
    
    if not xml.moneda.upper() in ["MXN", "MN", "PESOS", "MX"]:
        if "USD" in xml.moneda.upper() or xml.moneda.upper().startswith("D"):
            xml.es_dolares = True
        elif "EUR" in xml.moneda.upper() or xml.moneda.upper().startswith("E"):
            xml.es_euros = True
        else:
            if to_decimal(xml.tipocambio) > 1:
                xml.es_dolares = True

    return xml
