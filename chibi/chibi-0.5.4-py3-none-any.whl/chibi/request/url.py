from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from chibi.atlas import Chibi_atlas


class Chibi_url( str ):
    def __add__( self, other ):
        if isinstance( other, Chibi_url ):
            raise NotImplementedError
        if isinstance( other, str ) and other.startswith( '?' ):
            parts = list( urlparse( self ) )
            current = parse_qs( parts[4], keep_blank_values=True )
            news = parse_qs( other[1:], keep_blank_values=True )
            current.update( news )
            parts[4] = urlencode( current, doseq=True )
            return Chibi_url( urlunparse( parts ) )
        elif isinstance( other, dict ):
            parts = list( urlparse( self ) )
            current = parse_qs( parts[4], keep_blank_values=True )
            current.update( other )
            parts[4] = urlencode( current, doseq=True )
            return Chibi_url( urlunparse( parts ) )
        return Chibi_url( "/".join( self.split( '/' ) + [ other ] ) )
        # from chibi.file.snippets import join
        # return Chibi_url( urljoin( str( self ), str( other ) ) )

    def __eq__( self, other ):
        if isinstance( other, Chibi_url ):
            return str( self ) == str( other )
        if isinstance( other, str ):
            return str( self ) == other
        return False

    def __hash__( self ):
        return hash( str( self ) )

    @property
    def base_name( self ):
        return self.rsplit( '/', 1 )[-1]

    @property
    def params( self ):
        parts = list( urlparse( self ) )
        current = parse_qs( parts[4], keep_blank_values=True )
        for k, v in current.items():
            if isinstance( v, list ) and len( v ) == 1:
                current[k] = v[0]
        return Chibi_atlas( current )
