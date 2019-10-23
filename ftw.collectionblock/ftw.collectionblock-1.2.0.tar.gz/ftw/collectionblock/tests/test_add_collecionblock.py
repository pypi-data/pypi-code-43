from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from ftw.builder import Builder
from ftw.builder import create
from ftw.collectionblock.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class TestAddCollectionBlock(FunctionalTestCase):

    def setUp(self):
        super(TestAddCollectionBlock, self).setUp()
        self.grant('Manager')

        self.page = create(Builder('sl content page').titled(u'Test Page'))

    @browsing
    def test_add_collection_block(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('Collection block')
        title = u'A collection block'
        browser.fill({'Title': title, 'Show title': True})
        browser.find_button_by_label('Save').click()
        self.assertTrue(
            len(browser.css('.ftw-collectionblock-collectionblock')),
            'Expect on collection block')

        # Since there is no query configured, there should be no result
        self.assertEquals(u'No content available',
                          browser.css('.sl-block-content p').first.text)

    @browsing
    def test_show_title(self, browser):
        collectionblock = create(Builder('sl collectionblock')
                                 .titled(u'Not visible')
                                 .within(self.page))

        browser.login().visit(self.page)
        self.assertFalse(
            len(browser.css('.ftw-collectionblock-collectionblock h2')),
            'Expect no title on collection block')

        collectionblock.show_title = True
        transaction.commit()

        browser.visit(self.page)
        self.assertEquals(
            u'Not visible',
            browser.css('.ftw-collectionblock-collectionblock h2').first.text)

    @browsing
    def test_show_result_with_default_query(self, browser):
        create(Builder('sl collectionblock')
               .titled(u'A collectionblock')
               .within(self.page)
               .with_default_query())

        # The default query shows all Simplelayout Contentpages
        browser.login().visit(self.page)
        self.assertEquals(
            1,
            len(browser.css('.odd')))
        self.assertEquals(
            self.page.Title(),
            browser.css('.documentFirstHeading').first.text)

    @browsing
    def test_detail_view_on_collectionblock(self, browser):
        collectionblock = create(Builder('sl collectionblock')
                                 .titled(u'A collectionblock')
                                 .within(self.page)
                                 .with_default_query())
        browser.login().visit(self.page)
        browser.css('.collection-more').first.click()
        self.assertEquals(
            '{0}/listing_view'.format(collectionblock.absolute_url()),
            browser.url)
            
        self.assertEquals(
            [{'Title': 'Test Page',
              'Creator': 'test-user',
              'Type': 'ContentPage',
              'ModificationDate': browser.css('tbody tr td')[3].text}],
            browser.css('table.sortable').first.dicts())

    @browsing
    def test_custom_more_label(self, browser):
        collectionblock = create(Builder('sl collectionblock')
                                 .titled(u'A collectionblock')
                                 .within(self.page)
                                 .with_default_query())

        browser.login().visit(self.page)
        self.assertEquals(u'More',
                          browser.css('.collection-more').first.text)

        collectionblock.more_link_label = u'Even more'
        transaction.commit()

        browser.visit(self.page)
        self.assertEquals(u'Even more',
                          browser.css('.collection-more').first.text)

    @browsing
    def test_NO_rss_on_collectionblock_if_disabled(self, browser):
        create(Builder('sl collectionblock')
               .titled(u'A collectionblock')
               .having(show_rss_link=True)
               .within(self.page)
               .with_default_query())

        browser.login().visit(self.page)
        self.assertFalse(len(browser.css('.collection-rss')),
                         'RSS is no enabled, so no rss link should be there')

    @browsing
    def test_rss_on_collectionblock(self, browser):
        self._enable_feeds()
        collectionblock = create(Builder('sl collectionblock')
                                 .titled(u'A collectionblock')
                                 .having(show_rss_link=True)
                                 .within(self.page)
                                 .with_default_query())

        browser.login().visit(self.page)
        browser.css('.collection-rss').first.click()
        self.assertEquals(
            '{0}/RSS'.format(collectionblock.absolute_url()),
            browser.url)

    def _enable_feeds(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        settings.allowed = True
        settings.default_enabled = True
        transaction.commit()

    @browsing
    def test_block_amount_limit(self, browser):
        """
        This test makes sure that the collection block only renders
        the amount of items configured on the block.
        """
        create(Builder('sl content page').titled(u'Page 2'))
        create(Builder('sl content page').titled(u'Page 3'))

        create(Builder('sl collectionblock')
               .titled(u'A collectionblock')
               .within(self.page)
               .having(block_amount=2)
               .with_default_query())

        browser.login().visit(self.page)
        self.assertEquals(
            1,
            len(browser.css('.even'))
        )

    @browsing
    def test_is_table(self, browser):
        create(Builder('sl content page').titled(u'Page 2'))
        create(Builder('sl content page').titled(u'Page 3'))

        create(Builder('sl collectionblock')
               .titled(u'A collectionblock')
               .within(self.page)
               .having(block_amount=2)
               .with_default_query())

        browser.login().visit(self.page)

        self.assertEquals(
            [{'Title': 'Test Page',
              'Creator': 'test-user',
              'Type': 'ContentPage',
              'ModificationDate': browser.css('tbody tr td')[3].text},
             {'Title': 'Page 2',
              'Creator': 'test-user',
              'Type': 'ContentPage',
              'ModificationDate': browser.css('tbody tr td')[3].text}],
            browser.css('table.sortable').first.dicts())
