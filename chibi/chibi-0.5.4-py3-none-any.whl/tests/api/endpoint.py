import json

from unittest import TestCase
from unittest.mock import patch, ANY
from vcr_unittest import VCRTestCase

from chibi.api import Endpoint
from chibi.api.endpoint import GET, POST
from chibi.atlas import Chibi_atlas


class Endpoint_test( Endpoint, GET, POST ):
    url = 'http://a.4cdn.org/{board}/threads.json'


class Endpoint_get_post( Endpoint, GET, POST ):
    pass


class Test_endpoint_4chan_wallpaper_board( VCRTestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_get_post( 'http://a.4cdn.org/w/threads.json' )


class Test_endpoint_4chan_thread( VCRTestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_get_post( 'http://a.4cdn.org/{board}/threads.json' )


class Test_endpoint_4chan_thread_with_host( TestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_test(
            'http://a.4cdn.org/{board}/threads.json', host='other_host' )


class Test_endpoint_4chan_thread_headers( TestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_test(
            'http://a.4cdn.org/{board}/threads.json',
            headers={ 'Content-type': 'application/json' } )


class Test_endpoint_4chan_thread_with_proxy( TestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_test(
            'http://a.4cdn.org/w/threads.json',
            proxy={ 'http': 'some_proxie' } )


class Test_endpoint_class( VCRTestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_test()


class Test_get( Test_endpoint_4chan_wallpaper_board ):
    def test_response_should_be_200( self ):
        response = self.endpoint.get()
        self.assertEqual( response.status_code, 200 )
        self.assertIsInstance( response.headers, Chibi_atlas )
        self.assertIsInstance( response.body, str )
        self.assertIsInstance( response.native, list )
        self.assertListEqual( json.loads( response.body ), response.native )


class Test_init:
    def test_the_url_in_the_insntace_should_no_be_none( self ):
        self.assertIsNotNone( self.endpoint.assigned_url )


class Test_format:
    def test_should_create_another_instance_of_endpoint( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertIsNot( new_endpoint, self.endpoint )

    def test_should_change_the_url( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertEqual(
            new_endpoint.format_url, 'http://a.4cdn.org/w/threads.json' )


class Test_instance( Test_endpoint_4chan_thread, Test_format, Test_init ):
    pass


class Test_format_class( Test_endpoint_class, Test_format, Test_init ):
    pass


class Test_proxy( Test_endpoint_4chan_thread_with_proxy ):
    @patch( 'requests.get' )
    def test_request_should_use_proxie_in_requests_get( self, requests_get ):
        self.endpoint.get()
        requests_get.assert_called_with(
            ANY, proxies=self.endpoint.proxy, headers=None, params={} )

    @patch( 'requests.post' )
    def test_request_should_use_proxie_in_requests_post( self, requests_post ):
        self.endpoint.post()
        requests_post.assert_called_with(
            ANY, proxies=self.endpoint.proxy, data=None, headers=None )

    def test_assing_a_proxy_is_no_a_dict_should_raise_typeerror( self ):
        with self.assertRaises( TypeError ):
            self.endpoint.proxy = "some_proxy"

    def test_when_the_dict_have_values_with_None_or_false_should_return_None(
            self ):
        self.endpoint.proxy = { "None": None }
        self.assertIsNone( self.endpoint.proxy )
        self.endpoint.proxy = { "false": False }
        self.assertIsNone( self.endpoint.proxy )


class Test_hosts(
        Test_endpoint_4chan_thread_with_host, Test_init ):
    def test_should_create_another_instance_of_endpoint( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertIsNot( new_endpoint, self.endpoint )

    def test_should_change_the_url( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertEqual(
            new_endpoint.format_url, 'http://other_host/w/threads.json' )


class Test_headers(
        Test_endpoint_4chan_thread_headers, Test_init ):

    def test_should_create_another_instance_of_endpoint( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertIsNot( new_endpoint, self.endpoint )

    def test_the_new_instance_should_have_the_same_headers( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertEqual( new_endpoint._headers, self.endpoint._headers )
