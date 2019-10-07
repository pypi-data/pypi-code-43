import unittest

from autotrader_crawler.crawler import _index_page_url, pull_page, parse_index_page, pull_details_page
from test.sample import SAMPLE_PAGE


class MyTestCase(unittest.TestCase):
    def test_can_make_sample_index_page_url(self):
        self.assertEqual(_index_page_url(3, 'N1C 4AH'),
                         'https://www.autotrader.co.uk/results-car-search?sort=sponsored&radius=1500&postcode=N1C+4AH&onesearchad=Used&onesearchad=Nearly+New&make=PORSCHE&model=PANAMERA&writeoff-categories=on&page=3')

    def test_can_retrieve_sample_page(self):
        page = pull_page(1, 'N1C 4AG')
        self.assertIsNotNone(page)
        self.assertIsNotNone(page['html'])

    def test_can_extract_listing_links_from_sample_page(self):
        self.assertEqual(
            frozenset({'201904056639410',
                       '201905117852537',
                       '201906219242547',
                       '201906259399630',
                       '201906289507830',
                       '201907250430713',
                       '201908050811645',
                       '201908090958000',
                       '201908271568643',
                       '201909212476563',
                       '201909252598088',
                       '201909252617566'}),
            parse_index_page(SAMPLE_PAGE).advert_ids
        )

    def test_can_determine_there_is_a_next_page_from_sample_page(self):
        self.assertEqual(parse_index_page(SAMPLE_PAGE).has_next_listing_page, True)

    def test_get_a_details_page(self):
        index_page = parse_index_page(pull_page(1, 'N1C 4AG')['html'])
        details_page = pull_details_page(next(iter(index_page.advert_ids)))
        self.assertIsNotNone(details_page)

if __name__ == '__main__':
    unittest.main()
