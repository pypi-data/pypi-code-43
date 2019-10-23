from ftw.builder import Builder
from ftw.builder import create
from ftw.contentnav.testing import FTW_CONTENTNAV_FUNCTIONAL_TESTING
from plone.dexterity.fti import DexterityFTI
from Products.Five.browser import BrowserView as View
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager


class TestContentNavViewlet(TestCase):

    layer = FTW_CONTENTNAV_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        # add sample fti
        self.fti = DexterityFTI('Sample')
        self.fti.klass = 'plone.dexterity.content.Container'
        self.fti.schema = \
            'ftw.contentnav.tests.test_content_categorie_behavior.ISampleDX'
        self.fti.behaviors = (
            'ftw.contentnav.behaviors.content_categories.IContentCategories', )

        self.portal.portal_types._setObject('Sample', self.fti)

    def _get_viewlet(self, obj):
        view = View(obj, obj.REQUEST)
        manager_name = 'plone.belowcontentbody'
        manager = queryMultiAdapter(
            (obj, obj.REQUEST, view),
            IViewletManager,
            manager_name)

        self.failUnless(manager)

        # Set up viewlets
        manager.update()
        name = 'ftw.contentnav.contentnavlisting'
        return [v for v in manager.viewlets if v.__name__ == name]

    def test_viewlet_with_one_category(self):
        folder = create(Builder('sample'))
        content = create(Builder('sample')
                         .titled('Democontent')
                         .within(folder)
                         .having(content_categories=(u'WITH unicode \xe4', )))

        viewlet = self._get_viewlet(folder)[0]
        self.assertTrue(viewlet.available())

        self.assertIn(
            ('WITH unicode \xc3\xa4',
                [('Democontent', content.absolute_url(), '')]),
            viewlet.get_content())

    def test_viewlet_with_multiple_categories(self):
        folder = create(Builder('sample'))
        content = create(Builder('sample')
                         .titled('Democontent')
                         .within(folder)
                         .having(content_categories=(
                             u'WITH unicode \xe4', u'WITHOUT unicode')))

        viewlet = self._get_viewlet(folder)[0]
        self.assertTrue(viewlet.available())

        self.assertIn(
            ('WITH unicode \xc3\xa4',
                [('Democontent', content.absolute_url(), '')]),
            viewlet.get_content())

        self.assertIn(
            ('WITHOUT unicode',
                [('Democontent', content.absolute_url(), '')]),
            viewlet.get_content())

    def test_viewlet_without_categories(self):
        folder = create(Builder('sample'))
        create(Builder('sample')
               .titled('Democontent')
               .within(folder)
               .having(content_categories=(tuple())))

        viewlet = self._get_viewlet(folder)[0]
        self.assertIs(False, viewlet.available())

    def test_adding_new_category_using_the_new_categories_field(self):
        folder = create(Builder('sample'))
        content = create(Builder('sample')
                         .titled('Democontent')
                         .within(folder)
                         .having(new_content_categories=(u'WITH \xe4', )))

        viewlet = self._get_viewlet(folder)[0]

        self.assertTrue(viewlet.available())

        self.assertIn(
            ('WITH \xc3\xa4',
                [('Democontent', content.absolute_url(), '')]),
            viewlet.get_content())
