from tests.snippet.files import Test_with_files
import yaml
from chibi.file import Chibi_file


class Test_chibi_file_yaml( Test_with_files ):
    def setUp( self ):
        super().setUp()
        self.chibi_file = Chibi_file( self.files[0] )
        self.data = { 'a': 'a' }
        self.yaml_data = yaml.dump( self.data )

    def test_should_can_write_and_read_yaml( self ):
        whole_file = "".join( self.chibi_file.chunk() )
        self.assertFalse( whole_file, "el archivo no esta vacio" )
        self.chibi_file.write_yaml( self.data )
        whole_file = "".join( self.chibi_file.chunk() )
        self.assertEqual( whole_file, self.yaml_data )

        result = self.chibi_file.read_yaml()
        self.assertIsInstance( result, dict )
        self.assertEqual( result, self.data )

    def test_should_can_write_and_read_yaml_safe( self ):
        whole_file = "".join( self.chibi_file.chunk() )
        self.assertFalse( whole_file, "el archivo no esta vacio" )
        self.chibi_file.write_yaml( self.data, is_safe=True )
        whole_file = "".join( self.chibi_file.chunk() )
        self.assertEqual( whole_file, self.yaml_data )

        result = self.chibi_file.read_yaml()
        self.assertIsInstance( result, dict )
        self.assertEqual( result, self.data )
