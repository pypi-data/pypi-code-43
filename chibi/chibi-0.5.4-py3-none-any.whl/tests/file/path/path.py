import random
from unittest import TestCase
from unittest.mock import patch
import os

from faker import Factory as Faker_factory

from chibi.file import Chibi_file
from chibi.file.path import Chibi_path
from chibi.file.snippets import join, exists, ls, file_dir
from tests.snippet.files import Test_with_files


faker = Faker_factory.create()


class Test_path( Test_with_files ):
    def setUp( self ):
        super().setUp()
        self.path = Chibi_path( self.root_dir )

    def test_can_add_path_and_str( self ):
        dirs = ls( self.root_dir )
        for d in dirs:
            result = self.path + d
            self.assertEqual(
                result, os.path.join( str( self.path ), str( d ) ) )

    def test_ls_work( self ):
        dirs = list( self.path.ls() )
        self.assertGreaterEqual( len( dirs ), 1 )

    def test_ls_return_chibi_path( self ):
        dirs = list( self.path.ls() )
        self.assertGreaterEqual( len( dirs ), 1 )
        for d in dirs:
            self.assertIsInstance( d, Chibi_path )

    def test_find_work( self ):
        result = list( self.path.find() )
        for l in self.path.ls():
            self.assertIn( l, result )

    def test_mkdir_should_create_the_folder( self ):
        new_dir = Chibi_path( self.dirs[0] ) + 'asdf'
        if exists( new_dir ):
            self.fail(
                "el directiorio {} ya existe usar"
                "otro nombre".format( new_dir ) )
        new_dir.mkdir()
        if not exists( new_dir ):
            self.fail(
                "no se creo el directorio {} ".format( new_dir ) )

    def test_copy_folder_should_copy_all_folder( self ):
        dest = Chibi_path( self.root_dir ) + 'hola'
        self.assertFalse( exists( dest ) )
        source = Chibi_path( self.folder_with_files_with_content )
        source.copy( dest )
        self.assertTrue( exists( dest ) )

        self.assertEqual(
            len( set( ls( source ) ) ), len( set( ls( dest ) ) ) )

    def test_copy_to_a_existen_dir_should_override_the_current_files( self ):
        dest = Chibi_path( self.root_dir ) + 'hola'
        source = Chibi_path( self.folder_with_files_with_content )
        source.copy( dest )
        source.copy( dest )

    def test_copy_file_should_copy_the_file( self ):
        source = Chibi_path( random.choice( self.files_with_content ) )
        dest = Chibi_path( self.root_dir ) + faker.file_name()
        self.assertFalse( exists( dest ) )

        source.copy( dest, verbose=False )
        self.assertTrue( exists( dest ) )
        s = Chibi_file( source )
        d = Chibi_file( dest )
        self.assertEqual( s.file.read(), d.file.read() )

    def test_when_delete_a_file_should_no_exists( self ):
        path = Chibi_path( random.choice( self.files ) )
        self.assertTrue( exists( path ) )
        path.delete()
        self.assertFalse( exists( path ) )

    def test_whe_delete_a_dir_should_removed( self ):
        path = Chibi_path( random.choice( self.dirs ) )
        self.assertTrue( exists( path ) )
        path.delete()
        self.assertFalse( exists( path ) )


class Test_path_with_files( Test_with_files ):
    def test_if_path_is_a_file_should_only_use_the_dir( self ):
        for f in self.files:
            d = file_dir( f )
            p_f = Chibi_path( f )
            self.assertEqual( p_f + "another", os.path.join( d, 'another' ) )


class Test_path_relative( TestCase ):
    def test_can_add_path_and_str( self ):
        path = Chibi_path( '/usr/var/log' )
        result = path.relative_to( '/usr/var' )
        self.assertEqual( 'log', result )


class Test_path_chown( Test_with_files ):
    @patch( 'chibi.file.snippets.print' )
    def test_verbose_when_no_change_the_owners( self, print ):
        f = Chibi_path( self.files[0] )
        current_stat = f.properties

        f.chown()

        output = print.call_args_list[0][0][0]

        self.assertIn( 'permanece', output )
        self.assertIn(
            '{}:{}'.format(
                current_stat.user.name, current_stat.group.name ),
            output )


class Test_path_chmod( Test_with_files ):
    def test_verbose_when_no_change_the_owners( self ):
        f = Chibi_path( self.files[0] )
        current_stat = f.properties

        f.chmod( 0o755 )
        new_stat = f.properties
        self.assertNotEqual( current_stat.mode, new_stat.mode )


class Test_path_extension( Test_with_files ):
    def test_should_replace_the_extension( self ):
        f = Chibi_path( self.files[0] )
        self.assertFalse( f.endswith( '.ext' ) )
        f = f.replace_extensions( 'ext' )
        self.assertTrue( f.endswith( '.ext' ) )

    def test_should_add_the_extension( self ):
        f = Chibi_path( self.files[0] )
        self.assertFalse( f.endswith( '.ext' ) )
        f = f.add_extensions( 'ext' )
        self.assertTrue( f.endswith( '.ext' ) )


class Test_move( Test_with_files ):
    def test_when_move_a_empty_file_should_create_a_new_empty_file( self ):
        file = Chibi_path( random.choice( self.files ) )
        dest = Chibi_path( self.root_dir ) + faker.file_name()
        self.assertFalse( dest.exists )

        file.move( dest )

        self.assertFalse( file.exists )
        with open( str( dest ) ) as file_dest:
            self.assertFalse( file_dest.read() )

    def test_move_file_to_folder( self ):
        file = Chibi_path( random.choice( self.files ) )
        dest = Chibi_path( random.choice( self.dirs ) )

        file.move( dest )

        self.assertFalse( file.exists )
        self.assertTrue( dest.exists )

    def test_move_folder_to_another_another_name( self ):
        folder = Chibi_path( random.choice( self.dirs ) )
        dest = Chibi_path( self.root_dir ) + faker.name()

        folder.move( dest )

        self.assertFalse( folder.exists )
        self.assertTrue( dest.exists )


class Test_contains( Test_with_files ):
    def test_child_path_parent_path_should_be_true( self ):
        child = Chibi_path( random.choice( self.files ) )
        parent = Chibi_path( self.root_dir )
        self.assertIn( child, parent )

    def test_parent_in_child_should_be_false( self ):
        child = Chibi_path( random.choice( self.files ) )
        parent = Chibi_path( self.root_dir )
        self.assertNotIn( parent, child )


class Test_made_safe( Test_with_files ):
    def test_should_clean_the_characters( self ):
        path = Chibi_path( 'asdf*asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf<asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf>asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf:asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf"asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf|asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf?asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
        path = Chibi_path( 'asdf?*<>asdf' ).made_safe()
        self.assertEqual( 'asdfasdf', path )
