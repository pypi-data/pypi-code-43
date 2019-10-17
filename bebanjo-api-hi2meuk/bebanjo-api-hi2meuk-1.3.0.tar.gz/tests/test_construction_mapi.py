from unittest import TestCase
from bebanjo.things import Fetcher
from bebanjo import MovidaAPI
from .utils import object_from_file


class TestMapiInvalidConstruction(TestCase):

    def test_movida_api_no_env_or_url(self):
        with self.assertRaises(ValueError) as cm:
            _ = MovidaAPI()
        msg = cm.exception.args[0]
        assert 'url' in msg
        assert 'env' in msg

    def test_movida_api_bad_url(self):
        with self.assertRaises(ValueError) as cm:
            _ = MovidaAPI(url='http:bad')
        msg = cm.exception.args[0]
        assert 'url is invalid' in msg


class TestMapiValidConstruction(TestCase):

    def test_movida_api_url_explicit_staging(self):
        mapi = MovidaAPI(url=None, env='staging')
        assert mapi.url == 'https://staging-movida.bebanjo.net/api'

    def test_movida_api_url_implicit_staging(self):
        mapi = MovidaAPI('staging')
        assert mapi.url == 'https://staging-movida.bebanjo.net/api'

    def test_movida_api_url_preproduction(self):
        mapi = MovidaAPI('preproduction')
        assert mapi.url == 'https://preproduction-movida.bebanjo.net/api'

    def test_movida_api_url_production(self):
        mapi = MovidaAPI('production')
        assert mapi.url == 'https://movida.bebanjo.net/api'

    def test_mapi_properties(self):
        mapi = MovidaAPI('production')
        with self.assertRaises(AttributeError):
            _ = mapi.metadata
        assert mapi.summary_url == '/'
        assert isinstance(mapi.titles, Fetcher)

    def test_mapi_from_file_properties(self):
        mapi = object_from_file('movida_api.xml', '')
        with self.assertRaises(AttributeError):
            _ = mapi.metadata
