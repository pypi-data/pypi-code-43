from ftw.builder import Builder
from ftw.builder import create
from ftw.collectionblock.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestHideMoreLinkSetting(FunctionalTestCase):

    def setUp(self):
        super(TestHideMoreLinkSetting, self).setUp()
        self.grant('Manager')

        self.page = create(Builder('sl content page').titled(u'A page'))

    @browsing
    def test_more_link_is_visible_when_option_is_checked(self, browser):
        create(Builder('sl collectionblock')
               .titled(u'A collectionblock')
               .having(show_more_link=True)
               .within(self.page)
               .with_default_query())

        browser.visit(self.page)

        self.assertEqual(
            ['More'],
            [item.text for item in browser.css('.collection-more')]
        )

    @browsing
    def test_more_link_is_hidden_when_option_is_unchecked(self, browser):
        create(Builder('sl collectionblock')
               .titled(u'A collectionblock')
               .having(show_more_link=False)
               .within(self.page)
               .with_default_query())

        browser.visit(self.page)

        self.assertEqual(
            [],
            [item.text for item in browser.css('.collection-more')]
        )
