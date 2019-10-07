from unittest import mock, TestCase
from parameterized import parameterized
from bebanjo import MovidaAPI
from bebanjo.error import InvalidResourceError
from bebanjo.things import Collection, Fetcher
from .utils import assert_send_body_calls_match, FileReader, object_from_file

# pylint: disable=line-too-long

NEW_TITLE_XML = 'title_new_1555.xml'

API_URL = 'http://localhost:8080/api'
mapi = MovidaAPI(url=API_URL)


class TestCreate(TestCase):

    def setUp(self):
        patcher = mock.patch('bebanjo.things.send_body')
        self.m_send_body = patcher.start()
        self.addCleanup(patcher.stop)

    def test_title_create_title(self):
        self.m_send_body.return_value = FileReader(NEW_TITLE_XML)
        new = mapi.titles.create({'name': 'John'})
        assert len(self.m_send_body.mock_calls) == 1
        assert_send_body_calls_match(
            self.m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/titles$',
            re_body=r'^<title><name>John</name></title>$',
        )
        assert new.id == 1555

    @parameterized.expand([
        ([50, 51, 52], 'http.*/api/platforms/5[012]', 3),
        (['api/platforms/123'], 'http.*/api/platforms/123', 1),
        (['/api/platforms/123'], 'http.*/api/platforms/123', 1),
        (['http://localhost/api/platforms/567'], 'http.*/api/platforms/567', 1),
    ])
    def test_create_target_platform_call(self, pls, exp_href, exp_cnt):
        # setup
        image = object_from_file('image_5001.xml', '/images/5001')
        self.m_send_body.return_value = FileReader('target_platform_p_66.xml')
        # act
        image.target_platforms.add_platforms(pls)
        # assert
        assert len(self.m_send_body.mock_calls) == exp_cnt
        assert_send_body_calls_match(
            self.m_send_body,
            re_method='^POST$',
            re_url=r'.*/api/images/5001/target_platforms$',
            re_body=f'^<target-platforms><link href="{exp_href}" rel="platform" /></target-platforms>$'
        )
        # same body response setup for all tests input variations
        # since target_platforms is type Fetcher, it is not updated
        assert isinstance(image.target_platforms, Fetcher)

    def test_add_target_platform_updates_self(self):
        # setup
        tps = object_from_file('target_platforms_p_50.xml', '/target_platforms')
        self.m_send_body.return_value = FileReader('target_platform_p_66.xml')
        assert isinstance(tps, Collection)
        assert len(tps) == 1
        assert list(tps)[0].platform.id == 50
        # act
        tps.add_platforms((66,))   # tuple itterable this time
        # assert
        collected = {tp.platform.id for tp in tps}
        assert collected == {50, 66}

    def test_raises_create_platform_on_non_target_platforms(self):
        title = object_from_file('title_1001_exp_m.xml', '/titles/1001')
        self.m_send_body.return_value = lambda: b'<root />'
        with self.assertRaises(InvalidResourceError):
            title.add_platforms([50, 51])

    def test_no_add_if_target_platform_exists(self):
        # setup
        target_platforms = object_from_file('target_platforms_p_50.xml', '/images/1234/target_platforms')
        self.m_send_body.return_value = FileReader('target_platforms_p_50.xml')
        # act
        # already contains member with platform id 50, so should skip adding this one
        target_platforms.add_platforms([52, 50, 51])
        # assert
        assert len(self.m_send_body.mock_calls) == 2
        assert_send_body_calls_match(
            self.m_send_body,
            re_method='^POST$',
            re_url=r'http.*api/images/1234/target_platforms$',
            re_body=f'^<target-platforms><link href="http.*/api/platforms/5[12]" rel="platform" /></target-platforms>$'
        )
