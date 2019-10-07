import contextlib
import json
import time
import urllib.parse
import urllib.request
from collections import namedtuple
from html.parser import HTMLParser


def pull_page(page_number):
    for attempt in range(5):
        try:
            with contextlib.closing(urllib.request.urlopen(_index_page_url(page_number))) as autotrader_response:
                return json.loads(autotrader_response.read().decode('utf-8'))
        except json.decoder.JSONDecodeError:
            time.sleep(10)
    else:
        raise


def pull_details_page(advert_id):
    with contextlib.closing(urllib.request.urlopen(
            'https://www.autotrader.co.uk/json/fpa/initial/' + advert_id)) as autotrader_response:
        return json.loads(autotrader_response.read().decode('utf-8'))


class _IndexPageHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.stack = []
        self.advert_ids = frozenset()
        self.next_link = []

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if self.stack == ['div', 'ul', 'li'] and len(list(
                filter(lambda attribute: attribute[0] == 'class' and attribute[1] == 'search-page__result',
                       attrs))) == 1:
            self.advert_ids = self.advert_ids | frozenset(
                list(map(lambda attribute: attribute[1],
                         filter(lambda attribute: attribute[0] == 'data-advert-id', attrs))))
        if self.stack == ['div', 'nav', 'ul', 'li', 'a'] and len(list(
                filter(lambda attribute: attribute[0] == 'class' and attribute[1] == 'pagination--right__active',
                       attrs))) == 1:
            self.next_link = self.next_link + list(
                map(lambda attribute: attribute[1], filter(lambda attribute: attribute[0] == 'href', attrs)))

    def handle_endtag(self, tag):
        self.stack.pop()


def parse_index_page(page_body):
    parser = _IndexPageHTMLParser()
    parser.feed(page_body)
    return namedtuple('Result', ['advert_ids', 'has_next_listing_page'])(
        advert_ids=parser.advert_ids,
        has_next_listing_page=len(parser.next_link) > 0
    )


def _index_page_url(page_number):
    return urllib.parse.urlunparse((
        'https',
        'www.autotrader.co.uk',
        'results-car-search',
        '',
        urllib.parse.urlencode(
            {'sort': 'sponsored', 'radius': '1500', 'postcode': 'N1C 4AG', 'onesearchad': ['Used', 'Nearly New'],
             'make': 'PORSCHE', 'model': 'PANAMERA', 'writeoff-categories': 'on', 'page': page_number}, doseq=True),
        ''
    ))
