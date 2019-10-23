from ftw.builder import Builder
from ftw.builder import create
from ftw.contentnav.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone import api
from plone.dexterity.fti import DexterityFTI
from Products.CMFCore.utils import getToolByName


class TestContentCategoriesBehavior(FunctionalTestCase):

    def setUp(self):
        super(TestContentCategoriesBehavior, self).setUp()
        # add sample fti
        self.fti = DexterityFTI('Sample')
        self.fti.schema = \
            'ftw.contentnav.tests.test_content_categorie_behavior.ISampleDX'
        self.fti.behaviors = (
            'ftw.contentnav.behaviors.content_categories.IContentCategories', )

        self.portal.portal_types._setObject('Sample', self.fti)

    def test_category_index(self):
        catalog = getToolByName(self.portal, 'portal_catalog')

        create(Builder('sample')
               .having(content_categories=(u'DEMO1', )))

        self.assertTrue(catalog({'get_content_categories': 'DEMO1'})[0])

    def test_category_index_umlauts(self):
        catalog = getToolByName(self.portal, 'portal_catalog')

        create(Builder('sample')
               .having(content_categories=(u'WITH unicode \xe4', )))

        unique_values = catalog.Indexes[
            'get_content_categories'].uniqueValues()

        self.assertIn("WITH unicode \xc3\xa4", unique_values)

    @browsing
    def test_adding_new_categories_only_for_managers(self, browser):
        content = create(Builder('sample')
                         .titled('Democontent'))

        user = create(Builder('user')
                      .with_roles('Site Administrator', on=content))

        browser.login(user.getId()).visit(content, view='@@edit')

        selector = \
            '#formfield-form-widgets-IContentCategories-new_content_categories'
        self.assertFalse(browser.css(selector),
                         'New categories field should no be visible.')

        browser.login().visit(content, view='@@edit')
        self.assertTrue(
            browser.css(selector),
            'New categories field should be visible.')

    @browsing
    def test_categories_from_other_contents_are_available(self, browser):
        categories = (u'Cat 1', u'Cat 2', 'Cat 3')
        create(Builder('sample')
               .titled('Democontent')
               .having(content_categories=categories))

        content = create(Builder('sample')
                         .titled('Democontent'))

        browser.login().visit(content, view='@@edit')

        selector = '#form-widgets-IContentCategories-' \
                   'content_categories input[type=checkbox]'

        self.assertEqual(
            3,
            len(browser.css(selector)),
            'Some categories are missing in the edit-form')

    @browsing
    def test_widget_strips_duplicate_categories(self, browser):
        self.grant('Manager')
        content = create(Builder('sample'))
        browser.login()
        browser.visit(content, view='@@edit')
        browser.forms['form'].fill({u'New categories': u'Test\n   Test\nTest   \n  Test '}).submit()

        catalog_tool = api.portal.get_tool('portal_catalog')
        unique_values = catalog_tool.Indexes['get_content_categories'].uniqueValues()
        self.assertEqual(
            ('Test',),
            tuple(unique_values)
        )
