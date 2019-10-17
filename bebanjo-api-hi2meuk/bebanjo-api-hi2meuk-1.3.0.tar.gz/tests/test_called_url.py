import re
from unittest import mock, TestCase
from datetime import datetime, timezone, timedelta
from parameterized import parameterized
import bebanjo
from .utils import object_from_file

TZ_BST = timezone(timedelta(hours=1), name='DST')
TZ_GMT = timezone(timedelta(), name='GMT')

mapi = bebanjo.MovidaAPI(env='staging')

# pylint: disable=no-member


class TestThingsFuncs(TestCase):

    @parameterized.expand([
        ('online', '2019-07-04', '2019-07-05', '2019-07-05'),
        ('online', '2019-07-04', '2019-07-05T10:10', '2019-07-05T10:10'),
        ('online', '2019-07-04', '2019-07-05T10:10Z', '2019-07-05T10:10Z'),
        ('online', '2019-07-04', datetime(2019, 7, 10, 1, 2, 3, 4), '2019-07-10T01:02'),
        ('online', '2019-07-04', datetime(2019, 7, 10, 1, 2), '2019-07-10T01:02'),
        ('online', '2019-07-04', datetime(2019, 1, 10, tzinfo=TZ_GMT), '2019-01-10T00:00+00:00'),
        ('online', '2019-07-04', datetime(2019, 7, 10, 13, tzinfo=TZ_BST), '2019-07-10T13:00+01:00')
    ])
    def test_pass_scope_opts_good(self, scp, frm, _to, expect_to):
        opts = []
        bebanjo.things.pass_scope((scp, frm, _to), opts)
        assert opts == ['scope=online', f'from={frm}', f'to={expect_to}']


class TestFetch(TestCase):

    def setUp(self):
        patcher = mock.patch('bebanjo.things._get', return_value=None)
        self.mock_get = patcher.start()
        self.addCleanup(patcher.stop)

    def assert_get_correct_url(self, re_url):
        assert re.match(re_url, self.mock_get.call_args[0][0]) is not None

# tests

    def test_get_title_url(self):
        for _id in (193094357485, '19938493758455'):
            mapi.titles.fetch(_id)
            self.assert_get_correct_url(f'.*/api/titles/{_id}$')

    def test_get_title_metadata_url(self):
        title = object_from_file('title_1001_exp_m.xml', '/titles/1001')
        title.metadata.fetch()
        self.assert_get_correct_url('.*/api/titles/1001/metadata$')

    def test_get_titles_url(self):
        mapi.titles.fetch()
        self.assert_get_correct_url('.*/api/titles$')

    def test_get_url_titles_exp_metadata(self):
        mapi.titles.fetch(1001, expand='metadata')
        self.assert_get_correct_url('.*/api/titles/1001[?]expand=metadata$')

    def test_get_url_title_ext_id(self):
        for _id in [93056, '93056']:
            mapi.titles.fetch(external_id=_id)
        self.assert_get_correct_url(f'.*/api/titles[?]external_id={_id}$')

    def test_get_titles_paginated_url(self):
        for page_num in (1, 111):
            mapi.titles.get_paginated(page=page_num)
        for per_page in (5, 500):
            mapi.titles.get_paginated(per_page=per_page)
        self.assert_get_correct_url(
            r'.*/api/titles[?]page=1+[&]pagination=true[&]per_page=50*$'
        )
