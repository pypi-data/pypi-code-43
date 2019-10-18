from django.db import models
from .settings import (
    CFDI_DB_TABLE, XML_DIR
)


class Cfdi(models.Model):
    cfdi_xml = models.TextField()
    cfdi_error = models.TextField()
    cfdi_qrcode = models.TextField()
    acuse_cancelacion = models.TextField()
    cfdi_uuid = models.CharField(max_length=255, blank=True)
    cfdi_fecha_timbrado = models.DateTimeField(null=True)
    cfdi_sello_digital = models.TextField()
    cfdi_no_certificado_sat = models.TextField()
    cfdi_sello_sat = models.TextField()
    cadena_original_complemento = models.TextField()
    cfdi_status = models.TextField()
    inicio_conexion_pac = models.DateTimeField()
    fin_conexion_pac = models.DateTimeField()
    inicio_timbrado = models.DateTimeField()
    fin_timbrado = models.DateTimeField()
    folio = models.IntegerField(null=True)
    serie = models.CharField(max_length=10)
    tipo_comprobante = models.CharField(max_length=2)

    @property
    def xml(self):
        return self.cfdi_xml

    def cancelar_cfdi(self, config, timbrado_prueba=None, v33=False):
        from .functions import obtener_cancelacion_cfdi_base
        from .classes import CFDI
        if not self.cfdi_uuid:
            raise ValueError("El recibo no tiene UUID.")

        cfdi = obtener_cancelacion_cfdi_base(
            config, 
            uuid=self.cfdi_uuid,
            xml=self.cfdi_xml,
            timbrado_prueba=timbrado_prueba, 
        )
        cancelado, error_cancelacion = cfdi.cancelar_cfdi()
        if cancelado:
            self.cancelado = True
            self.acuse_cancelacion = cfdi.acuse_cancelacion
            self.save()

        return [cancelado, error_cancelacion]

    class Meta:
        db_table = CFDI_DB_TABLE


    def get_total_tiempo_timbrado(self):
        if self.inicio_conexion_pac and self.fin_conexion_pac and self.inicio_timbrado and self.fin_timbrado:
            dif_conexion = (self.fin_conexion_pac - self.inicio_conexion_pac)
            dif_timbrado = (self.fin_timbrado - self.inicio_timbrado)
            dif = dif_conexion + dif_timbrado
            return "%s.%06d" % (dif.seconds, dif.microseconds)

    def set_folio(self):
        if not self.folio:
            instance = self.__class__.objects.filter(
                tipo_comprobante=self.tipo_comprobante,
                serie=self.serie,
            ).order_by("-folio").first()

            self.folio = (instance.folio + 1) if instance else 1

    def xml_name(self):
        if self.cfdi_uuid:
            return "%s.xml" % self.cfdi_uuid

        return "%s.xml" % (self.folio or self.id)

    def xml_path(self, clave):
        import os
        d = "%s/%s" % (XML_DIR, clave)
        if not os.path.exists(d):
            os.makedirs(d)

        return "%s/%s" % (d, self.xml_name())

    def crear_xml_timbrado(self, clave="dmspitic"):
        import codecs
        f = open(self.xml_path(clave=clave), 'w')
        #f.write( codecs.BOM_UTF8 )
        try:
            f.write(self.cfdi_xml)
        except:
            f.write(self.cfdi_xml.encode('utf-8'))
        f.close()

    def generar_xml(self, cfdi):

        self.tipo_comprobante = cfdi.TipoDeComprobante
        self.serie = cfdi.Serie
        if cfdi.Folio:
            self.folio = cfdi.Folio
        else:
            self.set_folio()
            cfdi.Folio = self.folio

        cfdi.generar_xml_v33()
        error_sello = cfdi.generar_sello()
        if error_sello:
            self.cfdi_status = error_sello
            self.save()
            return 
        cfdi.sellar_xml()
        timbrado = cfdi.timbrar_xml()
        #Se Guardan los tiempos de timbrado
        self.inicio_conexion_pac = cfdi.inicio_conexion_pac
        self.fin_conexion_pac = cfdi.fin_conexion_pac
        self.inicio_timbrado = cfdi.inicio_timbrado
        self.fin_timbrado = cfdi.fin_timbrado

        if not timbrado:
            self.cfdi_status = cfdi.cfdi_status
            self.cfdi_xml = cfdi.xml
            self.save()
        else:
            self.cfdi_xml = cfdi.cfdi_xml
            self.cfdi_qrcode = cfdi.cfdi_qrcode
            self.cfdi_sello_digital = cfdi.cfdi_sello_digital
            self.cfdi_uuid = cfdi.cfdi_uuid
            self.cfdi_sello_sat = cfdi.cfdi_sello_sat
            self.cadena_original_complemento = cfdi.cadena_original_complemento
            self.cfdi_fecha_timbrado = cfdi.cfdi_fecha_timbrado
            self.cfdi_no_certificado_sat = cfdi.cfdi_no_certificado_sat
            self.save()




