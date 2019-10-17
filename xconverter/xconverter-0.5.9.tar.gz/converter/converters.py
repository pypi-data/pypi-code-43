import io
import os
import logging
import re
import uuid
from datetime import datetime

from lxml import etree as ET

from converter.dar import DarFileHandler

logger = logging.getLogger(__name__)

APP_PATH = os.path.dirname(os.path.realpath(__file__))


class CovertionException(Exception):
    pass


class EruditPS2PDFError(CovertionException):
    pass


def texture2html(source, custom_styles=None, pagedjs_support=False):
    """
    param source: absolute path to the Texture .dar file
    """

    with DarFileHandler(source) as dfh:
        dfh.get_assets()
        converter = EruditPS2HTML(dfh.temp_article_path)

    return converter.transform(
        custom_styles=custom_styles, pagedjs_support=pagedjs_support
    )


def texture2pdf(source, custom_styles=None):
    """
    param source: absolute path to the Texture .dar file
    """

    from weasyprint import HTML

    with DarFileHandler(source) as dfh:
        assets_path = 'file://%s' % '/'.join(
            dfh.temp_article_path.split('/')[:-1])
        converter1 = EruditPS2HTML(
            dfh.temp_article_path, assets_path=assets_path)
        html_body = converter1.transform(
            custom_styles=custom_styles, pagedjs_support=False).decode('utf-8')
        html = HTML(string=html_body)
        result = html.write_pdf()

    return result


def eruditarticle2crossref(source):
    """
    param source: absolute path to the Erudit Article XML file
    """

    converter1 = EruditArticle2EruditPS(source)

    xml = io.BytesIO(converter1.transform())

    converter2 = EruditPS2Crossref(xml)

    return converter2.transform()


def eruditarticle2eruditps(source):
    """
    param source: absolute path to the Erudit Article XML file
    """

    converter = EruditArticle2EruditPS(source)

    return converter.transform()


def eruditarticle2html(source, custom_styles=None, pagedjs_support=False):
    """
    param source: absolute path to the Erudit Article XML file
    """

    converter1 = EruditArticle2EruditPS(source)

    xml = io.BytesIO(converter1.transform())

    converter2 = EruditPS2HTML(xml)

    return converter2.transform(
        custom_styles=custom_styles, pagedjs_support=pagedjs_support)


def eruditarticle2pdf(source, custom_styles=None):
    """
    param source: absolute path to the Erudit Article XML file
    """

    from weasyprint import HTML

    base_url = '/'.join([os.getcwd()] + str(source).split('/')[:-1])

    assets_path = 'file://%s' % base_url

    converter1 = EruditArticle2EruditPS(source)

    xml = io.BytesIO(converter1.transform())

    converter2 = EruditPS2HTML(xml, assets_path=assets_path)

    html_body = converter2.transform(
        custom_styles=custom_styles, pagedjs_support=False).decode('utf-8')

    html = HTML(string=html_body)

    try:
        result = html.write_pdf()
    except AssertionError as e:
        raise EruditPS2PDFError(str(e))

    return result


def eruditps2crossref(source):
    """
    param source: absolute path to the Erudit Publishing Schema XML file
    """

    converter = EruditPS2Crossref(source)

    return converter.transform()


def eruditps2eruditarticle(source):
    """
    param source: absolute path to the Erudit Publishing Schema XML file
    """

    converter = EruditPS2EruditArticle(source)

    return converter.transform()


def eruditps2html(source, custom_styles=None, pagedjs_support=False):
    """
    param source: absolute path to the Erudit Publishing Schema XML file
    """

    converter = EruditPS2HTML(source)

    return converter.transform(
        custom_styles=custom_styles, pagedjs_support=pagedjs_support)


def eruditps2pdf(source, custom_styles=None):
    """
    param source: absolute path to the Erudit Publishing Schema XML file
    """
    from weasyprint import HTML

    base_url = '/'.join([os.getcwd()] + str(source).split('/')[:-1])

    assets_path = 'file://%s' % base_url

    converter1 = EruditPS2HTML(source, assets_path=assets_path)

    html_body = converter1.transform(
        custom_styles=custom_styles, pagedjs_support=False).decode('utf-8')

    html = HTML(string=html_body)

    try:
        result = html.write_pdf()
    except AssertionError as e:
        raise EruditPS2PDFError(str(e))

    return result


class Converter:

    def __init__(self, source, assets_path=''):
        """
        param source: Source can be a BytesIO object or a path to file in the file system.
        """

        self.source = source
        self.source_etree = self._source_etree()
        self.assets_path = assets_path

    def distinct(self, _, nodes):
        """
        This method receive a list of values matched in a XPATH query and remove the
        duplicated values.
        This method must receive a list of text() and not xml elements.
        Everything != from string will be skiped.
        """

        values = [i for i in nodes if isinstance(i, str)]

        lst = ET.Element('list')

        for value in set(values):
            item = ET.Element('item')
            item.text = value
            lst.append(item)

        return lst

    def _register_functions(self, ns=None):

        ns = ET.FunctionNamespace(ns or None)
        ns['distinct'] = self.distinct

    def _source_etree(self):
        parser = ET.XMLParser(remove_blank_text=True)

        if isinstance(self.source, io.BytesIO) is True:
            raw_xml = self.source.read()
        else:
            with open(self.source, 'rb') as xml:
                raw_xml = xml.read()

        raw_xml = re.sub(r'xmlns=".*?"', '', raw_xml.decode('utf-8'))
        self.source = io.BytesIO(raw_xml.encode('utf-8'))

        xml_etree = ET.parse(self.source, parser)

        return xml_etree

    def transform(self, lxml_etree=False, remove_namespace=False):

        self._register_functions('converter')

        parser = ET.XMLParser(remove_blank_text=True)

        with open(os.path.join(APP_PATH, self.XSL), 'rb') as xslfile:
            xsl = ET.parse(xslfile, parser)

        transformer = ET.XSLT(xsl)

        xml = transformer(self.source_etree)

        ET.cleanup_namespaces(xml, top_nsmap=self.TOP_NSMAP)

        # Pretty Print
        xml = ET.tostring(
            xml,
            doctype=self.DOCTYPE_STRING,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8'
        )

        if remove_namespace is True:
            xml = re.sub(r'xmlns=".*?"', '', xml.decode('utf-8')).encode('utf-8')

        if lxml_etree is True:
            return ET.parse(io.BytesIO(xml), parser)

        return xml


class EruditPS2HTML(Converter):

    XSL = 'xsls/EruditPS2HTML/main.xsl'
    BASE_CSS = ['static/css/erudit/pages.css', 'static/css/erudit/base.css']
    DOCTYPE_STRING = '<!DOCTYPE html>'

    def transform(self, custom_styles=None, pagedjs_support=False):
        """
        param custom_style: List of paths for custom CSS files
        """

        self._register_functions('converter')

        parser = ET.XMLParser(remove_blank_text=True)

        with open(os.path.join(APP_PATH, self.XSL), 'rb') as xslfile:
            xsl = ET.parse(xslfile, parser)

        transformer = ET.XSLT(xsl)
        html = transformer(self.source_etree, assets_path="'%s'" % self.assets_path)

        if custom_styles:
            css_paths = self.BASE_CSS[1:] + custom_styles
        else:
            css_paths = self.BASE_CSS

        for css in css_paths:
            stylesheet = ET.Element('style')
            stylesheet.text = open(os.path.join(APP_PATH, css), 'r').read()
            head = html.find('head')
            head.append(stylesheet)

        if pagedjs_support is True:
            stylesheet = ET.Element('style')
            stylesheet.text = open(os.path.join(APP_PATH, 'static/pagedjs/preview.css'), 'r').read()
            script = ET.Element('script', src='https://unpkg.com/pagedjs@0.1.28/dist/paged.polyfill.js')
            head = html.find('head')
            head.append(stylesheet)
            head.append(script)

        return ET.tostring(html, pretty_print=True, encoding='utf-8', method="html", doctype=self.DOCTYPE_STRING)


class EruditArticle2EruditPS(Converter):

    XSL = 'xsls/EruditArticle2EruditPS/main.xsl'
    DOCTYPE_STRING = '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD v1.2 20190208//EN" "https://jats.nlm.nih.gov/archiving/1.2/JATS-archivearticle1.dtd">'
    COPYRIGHT_YEAR_REGEX = re.compile(r'[1,2][0-9]{3}')
    TOP_NSMAP = {
        'xlink': 'http://www.w3.org/1999/xlink',
        'mml': 'http://www.w3.org/1998/Math/MathML'
    }

    def issue_season(self, _, nodes):
        """
        param nodes: /article/admin/numero/pub/periode

        return: periode itens concatenated with hiphen
        """

        try:
            return '-'.join([i.text.lower() for i in nodes])
        except:
            return ''

    def issue_number(self, _, nodes):
        """
        param nodes: /article/admin/numero/nonumero

        return: nonumero itens concatenated with hiphen
        """

        try:
            return '-'.join([i.text for i in nodes])
        except:
            return ''

    def extract_trans_title_groups(self, _, nodes, language):
        """
        param nodes: /article/liminaire/grtitre
        param language: str # The original language of the text
        """

        if not nodes or ET.iselement(nodes[0]) is False or nodes[0].tag != 'grtitre':
            return

        trans_langs = [i for i in set(nodes[0].xpath('.//@lang')) if i != language]

        data = []

        for language in trans_langs:
            titreparal = nodes[0].findall("titreparal[@lang='%s']" % language)
            sstitreparal = nodes[0].findall("sstitreparal[@lang='%s']" % language)
            if not titreparal and not sstitreparal:
                continue

            ttg = ET.Element('trans-title-group')
            ttg.set('{http://www.w3.org/XML/1998/namespace}lang', language)
            for item in titreparal:
                item.tag = 'trans-title'
                del(item.attrib['lang'])
                ttg.append(item)

            for item in sstitreparal:
                item.tag = 'trans-subtitle'
                del(item.attrib['lang'])
                ttg.append(item)

            data.append(ttg)

        return data

    def extract_copyright_statement(self, _, nodes):
        """
        param nodes: /article/admin//droitsauteur
        """
        declaration = ET.Element('declaration')
        declaration.text = ''
        for node in nodes:
            if node.find('liensimple') is not None:  # Skip droitsauteur that contains links for the license
                continue
            declaration.text += ' %s' % ' '.join([i.strip() for i in node.itertext()])

        declaration.text = declaration.text.strip()

        if declaration.text != '':
            return declaration

        return []

    def extract_license_year(self, _, nodes):
        """
        param nodes: /article/admin//droitsauteur
        """
        year = ET.Element('annee')
        years = set()
        text = ''

        for node in nodes:
            # Extract year from element annee
            # retrive if found any occurency of element annee in any droitsauteur element
            annee = node.find('annee')
            if annee is not None:
                year.text = annee.text
                return year

            # build string with values in elements inside droitsauteur to extract years from the string in case the
            # element annee is not declared

            text += ' '.join([i for i in node.itertext()])

        years = list(set(self.COPYRIGHT_YEAR_REGEX.findall(text)))
        year.text = '-'.join(years)

        if year.text:
            return year

        return []

    def isodate_to_elements(self, _, nodes):

        try:
            iso_date = str(nodes[0].text).strip()
        except IndexError:
            return []

        try:
            dat = datetime.strptime(iso_date, '%Y-%m-%d')
            day = ET.Element('day')
            day.text = '%02d' % dat.day
            month = ET.Element('month')
            month.text = '%02d' % dat.month
            year = ET.Element('year')
            year.text = str(dat.year)
            return [day, month, year]
        except ValueError:
            try:
                dat = datetime.strptime(iso_date, '%Y-%m')
                month = ET.Element('month')
                month.text = '%02d' % dat.month
                year = ET.Element('year')
                year.text = str(dat.year)
                return [month, year]
            except ValueError:
                try:
                    dat = datetime.strptime(iso_date, '%Y')
                    year = ET.Element('year')
                    year.text = str(dat.year)
                    return [year]
                except ValueError:
                    return []

    def get_xref_id(self, _, nodes, affiliations):

        for affiliation in affiliations:

            institution = affiliation.find('institution')
            affid = affiliation.get('id')

            if institution is None or affid is None:
                continue

            if len(nodes) > 0 and institution.text == ''.join(nodes):
                return affid

        return ''

    def _register_functions(self, ns=None):

        super()._register_functions(ns=ns)

        ns = ET.FunctionNamespace(ns or None)

        ns['isodate-to-elements'] = self.isodate_to_elements
        ns['extract-license-year'] = self.extract_license_year
        ns['extract-copyright-statement'] = self.extract_copyright_statement
        ns['extract-trans-title-groups'] = self.extract_trans_title_groups
        ns['get-xref-id'] = self.get_xref_id
        ns['issue-number'] = self.issue_number
        ns['issue-season'] = self.issue_season


class EruditPS2EruditArticle(Converter):

    XSL = 'xsls/EruditPS2EruditArticle/main.xsl'
    DOCTYPE_STRING = ''
    TOP_NSMAP = {
        'xlink': 'http://www.w3.org/1999/xlink',
        'mml': 'http://www.w3.org/1998/Math/MathML'
    }

    def _register_functions(self, ns=None):

        ns = ET.FunctionNamespace(ns or None)


class EruditPS2Crossref(Converter):

    XSL = 'xsls/EruditPS2Crossref/main.xsl'
    DOCTYPE_STRING = ''
    TOP_NSMAP = {
        'ai': 'http://www.crossref.org/AccessIndicators.xsd',
        'xlink': 'http://www.w3.org/1999/xlink',
        'mml': 'http://www.w3.org/1998/Math/MathML',
        'jats': 'http://www.ncbi.nlm.nih.gov/JATS1',
    }

    def head(self, _, nodes):
        """
        param nodes: /

        return: Crossref Schema structure for the element head.
            <head>
                <doi_batch_id>d526d364-05e3-4e4e-ac89-111cb5e5253f</doi_batch_id>
                <timestamp>20190730104232</timestamp>
                <depositor>
                    <depositor_name/>
                    <email_address/>
                </depositor>
                <registrant/>
            </head>
        The depoditor name, email and registrant values are retrived from the
        following environment variables.
        depositor_name : CROSSREF_DEPOSITOR_NAME
        email_address : CROSSREF_DEPOSITOR_EMAIL_ADDRESS
        registrant : CROSSREF_REGISTRANT
        """

        head = ET.Element('head')

        doi_batch_id = ET.Element('doi_batch_id')
        doi_batch_id.text = str(uuid.uuid4())

        timestamp = ET.Element('timestamp')
        timestamp.text = str(datetime.now().strftime('%Y%m%d%H%M%S'))+'0500'

        head.append(doi_batch_id)
        head.append(timestamp)

        depositor = ET.Element('depositor')

        depositor_name = ET.Element('depositor_name')
        depositor_name.text = os.environ.get('CROSSREF_DEPOSITOR_NAME', 'anonymous')
        depositor.append(depositor_name)

        email_address = ET.Element('email_address')
        email_address.text = os.environ.get('CROSSREF_DEPOSITOR_EMAIL_ADDRESS', 'anonymous@email.com')
        depositor.append(email_address)

        head.append(depositor)

        registrant = ET.Element('registrant')
        registrant.text = os.environ.get('CROSSREF_REGISTRANT', 'anonymous')

        head.append(registrant)

        return head

    def _register_functions(self, ns=None):

        super()._register_functions(ns=ns)

        ns = ET.FunctionNamespace(ns or None)

        ns['head'] = self.head


class EruditArticle2TEI(Converter):

    XSL = 'xsls/EruditArticle2TEI/main.xsl'
    DOCTYPE_STRING = ''

    XSL = 'xsls/EruditPS2TEI/main.xsl'
    DOCTYPE_STRING = ''
