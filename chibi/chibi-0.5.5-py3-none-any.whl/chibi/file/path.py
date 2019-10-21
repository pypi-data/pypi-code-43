import distutils.dir_util
import logging
import os
import shutil
import re

import fleep


logger = logging.getLogger( "chibi.file.chibi_path" )


class Chibi_path( str ):
    def __new__( cls, *args, **kw ):
        args_2 = []
        for a in args:
            if '~' in a:
                a = os.path.expanduser( a )
            args_2.append( a )
        return str.__new__( cls, *args_2, **kw )

    def __add__( self, other ):
        """
        une el path con otro path o una cadena

        Parameters
        ==========
        other: str or Chibi_path

        Returns
        =======
        Chibi_path
        """
        if isinstance( other, self.__class__ ):
            if self.is_a_file:
                return self.dir_name + other

            return type( self )( os.path.join( str( self ), str( other ) ) )
        if isinstance( other, str ):
            return self + self.__class__( other )

    def __eq__( self, other ):
        if isinstance( other, Chibi_path ):
            return str( self ) == str( other )
        if isinstance( other, str ):
            return str( self ) == other
        return False

    def __hash__( self ):
        return hash( str( self ) )

    def __contains__( self, other ):
        if isinstance( other, Chibi_path ):
            return other.startswith( self )
        else:
            return super().__contains__( other )

    @property
    def is_a_folder( self ):
        """
        es una carpeta
        """
        from chibi.file.snippets import is_a_folder
        return is_a_folder( self )

    @property
    def is_a_file( self ):
        """
        es un archivo
        """
        from chibi.file.snippets import is_a_file
        return is_a_file( self )

    @property
    def dir_name( self ):
        """
        regresa la carpeta padre
        """
        from chibi.file.snippets import file_dir
        return self.__class__( file_dir( self ) )

    @property
    def base_name( self ):
        """
        regresa el nombre del archivo o de la carpeta
        """
        return Chibi_path( os.path.basename( self ) )

    def open( self ):
        """
        abre el archivo usando un chibi file
        """
        if self.is_a_folder:
            raise NotImplementedError
        from . import Chibi_file
        return Chibi_file( self )

    def relative_to( self, root ):
        from .snippets import get_relative_path
        return type( self )( get_relative_path( self, root=root ) )

    def mkdir( self, **kw ):
        """
        crea una carpeta en la direcion del chibi path
        """
        try:
            os.makedirs( self )
            logger.info( "se creo el directorio '{}'".format( self ) )
        except OSError:
            pass
        if kw:
            logger.warning(
                "mkdir de chibi path recibio parametros {}".format( kw ) )

    def move( self, dest ):
        """
        move the chibi path al destino
        """
        if self.is_a_file:
            if dest.is_a_folder:
                dest += self.base_name
        shutil.move( str( self ), str( dest ) )
        logger.info( "{} -> {}".format( self, dest ) )

    def copy( self, dest, **kw ):
        """
        copia el archivo o carpeta al destino
        """
        from.snippets import copy
        if self.is_a_file:
            copy( self, dest, **kw )
            return Chibi_path( dest )
        elif self.is_a_folder:
            distutils.dir_util.copy_tree( str( self ), str( dest ) )
            return Chibi_path( dest )

    def delete( self ):
        """
        elimina el archivo o la carpeta
        """
        from.snippets import delete
        delete( str( self ) )
        logger.info( 'delete "{}"'.format( self ) )

    def chown(
            self, verbose=True, user_name=None, group_name=None,
            recursive=False ):
        """
        cambia el duano del archivo o carpeta
        """
        from chibi.file.snippets import chown
        chown(
            self, user_name=user_name, group_name=group_name,
            recursive=recursive )

    def chmod( self, mod ):
        """
        cambia los attributos del archivo o carpeta
        """
        os.chmod( str( self ), mod )

    @property
    def properties( self ):
        from chibi.file.snippets import stat

        prop = stat( self )
        with open( self, 'rb' ) as f:
            info = fleep.get( f.read( 128 ) )

        prop.type = info.type[0] if info.type else None
        prop.extension = info.extension[0] if info.extension else None
        prop.mime = info.mime[0] if info.mime else None
        return prop

    @property
    def extension( self ):
        """
        regresa la extencion del archivo
        """
        if self.is_a_file:
            return self.properties.extension
        else:
            raise NotImplementedError

    def replace_extensions( self, *extensions ):
        """
        cambia la extencion del archivo
        """
        file_name, ext = os.path.splitext( self )
        extensions = ".".join( extensions )
        file_name = ".".join( ( file_name, extensions ) )
        return type( self )( file_name )

    def add_extensions( self, *extensions ):
        """
        agrega mas extenciones
        """
        file_name, ext = os.path.splitext( self )
        extensions = ".".join( extensions )
        file_name = ".".join( ( file_name, ext + extensions ) )
        return type( self )( file_name )

    def ls( self, dirs=True, files=True ):
        """
        regresa un generador con el listado de archivos y carpetas
        """
        from .snippets import ls, ls_only_dir, ls_only_files
        if dirs and files:
            return ls( self )
        elif dirs and not files:
            return ls_only_dir( self )
        elif not dirs and files:
            return ls_only_files( self )
        else:
            raise NotImplementedError

    def find( self, search_term=".*", dirs=True, files=True ):
        """
        busca archivos y carpetas usando una exprecion regular
        """
        if self.is_a_file:
            raise NotImplementedError(
                "no esta implementa buscar en un archivo" )
        from .snippets import find, find_only_files, find_only_folders
        if dirs and files:
            return find( self, search_term )
        elif dirs and not files:
            return find_only_folders( self, search_term )
        elif not dirs and files:
            return find_only_files( self, search_term )
        else:
            raise NotImplementedError

    @property
    def exists( self ):
        """
        revisa si el archivo o directorio existe

        Returns
        =======
        bool
        """
        from .snippets import exists
        return exists( str( self ) )

    def replace( self, *args, **kw ):
        return Chibi_path( super().replace( *args, **kw ) )

    def made_safe( self ):
        return Chibi_path( re.sub( r'[<>:"|?*]', '', str( self ) ) )
