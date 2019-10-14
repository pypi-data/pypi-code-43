import copy
import json
import mmap

import fleep
import yaml

from chibi.atlas import _wrap
from chibi.file.path import Chibi_path
from chibi.file.snippets import (
    exists, stat, check_sum_md5, read_in_chunks, base_name, file_dir,
    copy as copy_file,
)


class Chibi_file:
    def __init__( self, file_name ):
        self._file_name = file_name
        self._current_dir = file_dir( file_name )
        if not self.exists:
            self.touch()
        self.reread()

    def __str__( self ):
        return "file: '{}'".format( self.path )

    @property
    def file_name( self ):
        return base_name( self._file_name )

    @property
    def dir( self ):
        return self._current_dir

    @property
    def path( self ):
        return Chibi_path( self._file_name )

    @property
    def is_empty( self ):
        return self.properties.size == 0

    @property
    def properties( self ):
        prop = stat( self.path )
        with open( self.path, 'rb' ) as f:
            info = fleep.get( f.read( 128 ) )

        prop.type = info.type[0] if info.type else None
        prop.extension = info.extension[0] if info.extension else None
        prop.mime = info.mime[0] if info.mime else None
        return prop

    def __del__( self ):
        try:
            self.file.close()
        except AttributeError:
            pass

    def close( self ):
        self.file.close()

    def find( self, string_to_find ):
        if isinstance( string_to_find, str ):
            string_to_find = string_to_find.encode()
        with mmap.mmap(
                self.file.fileno(), 0, prot=mmap.PROT_READ ) as f:

            return f.find( string_to_find )

    def reread( self ):
        self.file = open( self.path, 'r' )

    def __contains__( self, string ):
        return self.find( string ) >= 0

    def append( self, string ):
        with open( self.path, 'a' ) as f:
            f.write( string )
        self.reread()

    def write( self, string ):
        if isinstance( string, ( bytes, bytearray ) ):
            with open( self.path, 'wb' ) as f:
                f.write( string )
        else:
            with open( self.path, 'w' ) as f:
                f.write( string )
        self.reread()

    def read( self ):
        """
        lee todo el archivo
        """
        result = self.file.read()
        self.reread()
        return result

    @property
    def file( self ):
        return self._file_content

    @file.setter
    def file( self, value ):
        try:
            old_file = self._file_content
            old_file.close()
        except AttributeError:
            pass
        self._file_content = value

    @property
    def exists( self ):
        return exists( self.path )

    def touch( self ):
        open( self.path, 'a' ).close()

    def copy( self, dest, verbose=True, **kw ):
        copy_file( self.path, dest, verbose=verbose, **kw )

    def chunk( self, chunk_size=4096 ):
        return read_in_chunks( self.path, 'r', chunk_size=chunk_size )

    def check_sum_md5( self, check_sum ):
        return check_sum_md5( self.path, check_sum )

    def read_json( self ):
        self.reread()
        return _wrap( json.load( self.file ) )

    def write_json( self, data ):
        self.write( json.dumps( data ) )

    def read_yaml( self ):
        self.reread()
        result = yaml.load( self.file, Loader=yaml.FullLoader )
        return _wrap( result )

    def write_yaml( self, data, is_safe=False ):
        if is_safe:
            self.write( yaml.safe_dump( data ) )
        else:
            self.write( yaml.dump( data ) )

    def __copy__( self ):
        return type( self )( self.path )

    def __eq__( self, other ):
        if isinstance( other, Chibi_file ):
            return self.path == other.path
        return False

    def __iadd__( self, other ):
        if ( isinstance( other, str ) ):
            self.append( other )
            return self
        if ( isinstance( other, Chibi_file ) ):
            if self == other:
                self += "".join( other.chunk() )
                return self

            other = copy.copy( other )
            for chunk in other.chunk():
                self += chunk
            return self
        self += str( other )
