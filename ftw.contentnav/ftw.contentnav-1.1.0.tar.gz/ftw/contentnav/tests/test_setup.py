from ftw.contentnav.testing import FTW_CONTENTNAV_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestPackageInstall(TestCase):

    layer = FTW_CONTENTNAV_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_package_installed(self):
        pid = 'ftw.contentnav'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertIn(
            pid, installed, 'package appears not to have been installed')

    def test_index_get_content_categories_installed(self):
        catalog = getToolByName(self.portal, "portal_catalog")
        self.assertIn('get_content_categories', catalog.indexes())

    def test_installed(self):
        portal_setup = getToolByName(self.portal, 'portal_setup')
        version = portal_setup.getLastVersionForProfile('ftw.contentnav:default')
        self.assertNotEqual(version, None, 'Maybe the metadata.xml is missing.')
        self.assertNotEqual(version, 'unknown', 'Maybe the metadata.xml is missing.')
