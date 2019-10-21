from chibi.file.snippets import exists
from chibi.file.temp import Chibi_temp_path
from chibi.file import Chibi_path
from tests.snippet.files import Test_with_files


class Test_path_temp( Test_with_files ):
    def test_when_is_delete_should_remove_the_folder( self ):
        path = Chibi_temp_path()
        path_str = str( path )
        self.assertTrue( exists( path ) )
        del path
        self.assertFalse( exists( path_str ) )

    def test_when_add_string_should_return_a_chibi_path( self ):
        path = Chibi_temp_path()
        result = path + "hello"
        self.assertIsInstance( result, Chibi_path )
        self.assertIn( str( path ), result )
        self.assertIn( "hello", result )
