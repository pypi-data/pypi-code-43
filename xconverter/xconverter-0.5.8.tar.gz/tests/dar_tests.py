import unittest
import os

from converter import dar

APP_PATH = os.path.dirname(os.path.realpath(__file__))


class TestManifest(unittest.TestCase):

    def setUp(self):

        with open(APP_PATH + '/fixtures/dar/manifest.xml', 'rb') as manifest:
            self.manifest = manifest.read()

    def test_instanciating_manifest(self):

        manifest = dar.Manifest(self.manifest)

        expected = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<dar>\n  <documents>\n    <document id="manuscript" type="article" path="texture.xml"/>\n  </documents>\n  <assets>\n    <asset id="fig1" type="image/jpg" path="image1.jpg"/>\n    <asset id="fig10" type="image/jpg" path="image10.jpg"/>\n    <asset id="fig2" type="image/jpg" path="image2.jpg"/>\n    <asset id="fig3" type="image/jpg" path="image3.jpg"/>\n    <asset id="fig4" type="image/jpg" path="image4.jpg"/>\n    <asset id="fig5" type="image/jpg" path="image5.jpg"/>\n    <asset id="fig6" type="image/jpg" path="image6.jpg"/>\n    <asset id="fig7" type="image/jpg" path="image7.jpg"/>\n    <asset id="fig8" type="image/jpg" path="image8.jpg"/>\n    <asset id="fig9" type="image/jpg" path="image9.jpg"/>\n  </assets>\n</dar>\n'

        self.assertEqual(manifest._manifest, expected)

    def test_documents(self):

        manifest = dar.Manifest(self.manifest)

        expected = [
            {
                "id": "manuscript",
                "type": "article",
                "path": "texture.xml"
            }
        ]

        self.assertEqual(manifest.documents, expected)

    def test_assets(self):

        manifest = dar.Manifest(self.manifest)

        expected = [
            {'id': 'fig1', 'type': 'image/jpg', 'path': 'image1.jpg'},
            {'id': 'fig10', 'type': 'image/jpg', 'path': 'image10.jpg'},
            {'id': 'fig2', 'type': 'image/jpg', 'path': 'image2.jpg'},
            {'id': 'fig3', 'type': 'image/jpg', 'path': 'image3.jpg'},
            {'id': 'fig4', 'type': 'image/jpg', 'path': 'image4.jpg'},
            {'id': 'fig5', 'type': 'image/jpg', 'path': 'image5.jpg'},
            {'id': 'fig6', 'type': 'image/jpg', 'path': 'image6.jpg'},
            {'id': 'fig7', 'type': 'image/jpg', 'path': 'image7.jpg'},
            {'id': 'fig8', 'type': 'image/jpg', 'path': 'image8.jpg'},
            {'id': 'fig9', 'type': 'image/jpg', 'path': 'image9.jpg'}
        ]

        self.assertEqual(manifest.assets, expected)
