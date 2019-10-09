import json
import unittest

from autotrader_crawler.crawler import _index_page_url, pull_page, parse_index_page, pull_details_page
from test.sample import SAMPLE_PAGE


class MyTestCase(unittest.TestCase):
    def test_can_make_sample_index_page_url(self):
        self.assertEqual(_index_page_url(3, 'N1C 4AH', 'ROBIN', 'RELIANT'),
                         'https://www.autotrader.co.uk/results-car-search?sort=sponsored&radius=1500&postcode=N1C+4AH&onesearchad=Used&onesearchad=Nearly+New&make=ROBIN&model=RELIANT&writeoff-categories=on&page=3')

    def test_can_retrieve_sample_page(self):
        page = pull_page(1, 'N1C 4AG', 'PORSCHE', 'PANAMERA')
        self.assertIsNotNone(page)
        self.assertIsInstance(page, type(str()))
        self.assertIsNotNone(json.loads(page)['html'])

    def test_can_extract_listing_links_from_sample_page(self):
        self.assertEqual(
            frozenset({'201901043649878',
                       '201903216133685',
                       '201905238259877',
                       '201908030762182',
                       '201908060859843',
                       '201908141144066',
                       '201908261525741',
                       '201909202432361',
                       '201909202433313',
                       '201910012818890',
                       '201910022857360',
                       '201910022868004',
                       '201910042971165'}),
            parse_index_page(SAMPLE_PAGE).advert_ids
        )

    def test_can_determine_there_is_a_next_page_from_sample_page(self):
        self.assertEqual(parse_index_page(SAMPLE_PAGE).has_next_listing_page, True)

    def test_get_a_details_page(self):
        index_page = parse_index_page(pull_page(1, 'N1C 4AG', 'PORSCHE', 'PANAMERA'))
        details_page = pull_details_page(next(iter(index_page.advert_ids)))
        self.assertIsNotNone(details_page)
        self.assertIsInstance(details_page, type(str()))

if __name__ == '__main__':
    unittest.main()
