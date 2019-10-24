import unittest
import os
import io

from lxml import etree

from converter import converters

APP_PATH = os.path.dirname(os.path.realpath(__file__))


class TestEruditArticle2EruditPS(unittest.TestCase):

    def setUp(self):

        self.conv = converters.EruditArticle2EruditPS(
            source=APP_PATH + '/fixtures/eruditarticle/document_eruditarticle.xml'
        )

        self.xml = self.conv.transform(lxml_etree=True, remove_namespace=True)

    def test_isodate_to_elements(self):

        origin = etree.Element('date')
        origin.text = '2014-06-26'

        result = self.conv.isodate_to_elements('dummy', [origin])

        self.assertEqual(result[0].text, '26')
        self.assertEqual(result[1].text, '06')
        self.assertEqual(result[2].text, '2014')
        self.assertEqual(len(result), 3)

    def test_isodate_to_elements_empty(self):

        result = self.conv.isodate_to_elements('dummy', [])

        self.assertEqual(result, [])

    def test_isodate_to_elements_year_and_month(self):

        origin = etree.Element('date')
        origin.text = '2014-06'

        result = self.conv.isodate_to_elements('dummy', [origin])

        self.assertEqual(result[0].text, '06')
        self.assertEqual(result[1].text, '2014')
        self.assertEqual(len(result), 2)

    def test_isodate_to_elements_year(self):

        origin = etree.Element('date')
        origin.text = '2014'

        result = self.conv.isodate_to_elements('dummy', [origin])

        self.assertEqual(result[0].text, '2014')
        self.assertEqual(len(result), 1)

    def test_isodate_to_elements_invalid_date(self):

        origin = etree.Element('date')
        origin.text = 'XXX'

        result = self.conv.isodate_to_elements('dummy', [])

        self.assertEqual(result, [])

    def test_extract_license_year_with_element_annee(self):
        """
        The Érudit Article XML has the element annee in droitsauteur
        <droitsauteur>Tous droits réservés © <nomorg>Approches inductives</nomorg>, <annee>2014</annee></droitsauteur>
        <droitsauteur>
          <liensimple xmlns:xlink="http://www.w3.org/1999/xlink" id="ls1" xlink:href="http://creativecommons.org/licenses/by-sa/3.0/" xlink:actuate="onRequest" xlink:show="replace" xlink:type="simple">
            <objetmedia flot="ligne">
              <image typeimage="forme" xlink:href="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" xlink:actuate="onLoad" xlink:show="embed" xlink:type="simple"/>
            </objetmedia>
          </liensimple>
        </droitsauteur>
        """
        year = etree.Element('annee')
        year.text = '2014'
        self.conv.source_etree.xpath("admin/droitsauteur")[0].append(year)

        result = self.conv.extract_license_year('dummy', self.conv.source_etree.xpath("admin/droitsauteur"))

        self.assertEqual(result.text, '2014')

    def test_extract_license_year_without_element_annee(self):
        """
        The Érudit Article XML has not the element annee in droitsauteur. The year is in some of the elements as text.
        <droitsauteur>Tous droits réservés © <nomorg>Approches inductives</nomorg>, 2014</droitsauteur>
        <droitsauteur>
          <liensimple xmlns:xlink="http://www.w3.org/1999/xlink" id="ls1" xlink:href="http://creativecommons.org/licenses/by-sa/3.0/" xlink:actuate="onRequest" xlink:show="replace" xlink:type="simple">
            <objetmedia flot="ligne">
              <image typeimage="forme" xlink:href="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" xlink:actuate="onLoad" xlink:show="embed" xlink:type="simple"/>
            </objetmedia>
          </liensimple>
        </droitsauteur>
        """
        result = self.conv.extract_license_year('dummy', self.conv.source_etree.xpath("admin/droitsauteur"))

        self.assertEqual(result.text, '2014')
