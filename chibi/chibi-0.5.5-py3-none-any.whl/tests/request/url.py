from chibi.request import Chibi_url
from unittest import TestCase


class Test_url( TestCase ):
    def setUp( self ):
        self.url = Chibi_url( "https://google.com" )


class Test_base_name( Test_url ):
    def test_base_name_should_return_the_last_part( self ):
        self.url = self.url + "1234567"
        base_name = self.url.base_name
        self.assertEqual( "1234567", base_name )


class Test_url_add( Test_url ):
    def test_can_add_parts( self ):
        self.assertIsInstance( self.url + "cosa", Chibi_url )
        self.assertEqual( "https://google.com/cosa", self.url + "cosa" )
        self.assertEqual(
            "https://google.com/cosa/cosa2", self.url + "cosa/cosa2" )
        self.assertEqual(
            "https://google.com/cosa/cosa2/cosa3",
            ( self.url + "cosa/cosa2" ) + "cosa3" )

    def test_add_a_query( self ):
        result = self.url + "?param1=value1"
        self.assertEqual( { 'param1': 'value1' }, result.params )
        self.assertEqual(
            { 'param1': 'value1', 'param2': 'value2' },
            ( result + "?param2=value2" ).params )

    def test_add_a_dict_should_add_the_query( self ):
        result = self.url + { 'param1': 'value1' }
        self.assertEqual( { 'param1': 'value1' }, result.params )

        result = result + { 'param2': 'value2' }
        self.assertEqual(
            { 'param1': 'value1', 'param2': 'value2' },
            result.params )

        result = self.url + { 'param1': 'value1', 'param2': 'value2' }
        self.assertEqual(
            { 'param1': 'value1', 'param2': 'value2' }, result.params )
