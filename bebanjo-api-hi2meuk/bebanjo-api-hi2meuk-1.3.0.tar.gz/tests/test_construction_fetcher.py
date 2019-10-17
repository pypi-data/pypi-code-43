from unittest import TestCase, mock
from bebanjo.utils import inspect
from bebanjo.things import Fetcher, Metadata
from .utils import object_from_file

# pylint: disable=protected-access


class TestTitleConstruction(TestCase):

    def test_title_no_metadata(self):
        title = object_from_file('title_1001.xml', '/titles/1001')
        assert not title.metadata  # empty metadata class Fetcher must tests false

    def test_title_construction(self):
        title = object_from_file('title_1001_exp_img.xml', '/titles/1001')
        assert title.id == 1001
        assert title['external_id'] == '63056'
        assert title['name'] == 'Winter Is Coming'
        assert isinstance(title.metadata, Metadata)
        assert len(title.metadata['subgenres']) == 2
        assert isinstance(title, Fetcher)
        assert isinstance(title.images, Fetcher)
        assert isinstance(title._meta1, dict)
        assert isinstance(title.metadata, (dict, Metadata))
        assert title.url == 'http://localhost:8080/api/titles/1001'
        assert title.summary_url == '/titles/1001'
        assert title.resource_type == 'title'
        assert title.id == 1001
        with self.assertRaises(KeyError):
            _ = title['id']

    @mock.patch('sys.stdout')
    def test_inspect(self, mock_std_out):
        title = object_from_file('title_1001_exp_m.xml', '/titles/1001')
        inspect(title)
        out_str = mock_std_out.mock_calls[0][1][0]
        assert r"Instance of Title (/titles/1001)" in out_str
        assert "> name: 'Winter Is Coming" in out_str
        assert "Metadata:" in out_str
        assert "> short_description" in out_str
        assert r"Getters:" in out_str
        assert "> images" in out_str


class TestFetcherFeatures(TestCase):

    def test_hop_schedule_schedulings(self):
        title = object_from_file('title_1001_exp_img.xml', '/titles/1001')
        assert isinstance(title.schedule, Fetcher)
        schedulings = title.schedule.add_link('schedulings')
        assert isinstance(schedulings, Fetcher)
        assert schedulings.url == title.url + '/schedule/schedulings'
