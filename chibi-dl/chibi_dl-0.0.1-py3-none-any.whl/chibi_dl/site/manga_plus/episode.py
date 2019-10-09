import logging
import re
import shutil

from chibi.file import Chibi_path

from chibi_dl.site.base.site import Site


logger = logging.getLogger( "chibi_dl.sites.manga_plus.episode" )


class Episode( Site ):
    def download( self, path ):
        logger.info(
            "iniciando la descarga de las {} imagenes del capitulo {}".format(
                len( self.images_urls ), self.number,
            ) )
        raise NotImplementedError

    def compress( self, path_ouput, path_input, format="zip" ):
        logger.info( "comprimiendo capitulo usando {}".format( format ) )
        result = Chibi_path( shutil.make_archive(
            path_ouput + self.number, format, path_input ) )
        expected = result.replace_extensions( "cbz" )
        result.move( expected )
        return expected

    @property
    def file_name( self ):
        return "{}.{}".format( self.number, "cbz" )

    @property
    def number( self ):
        re_float = re.compile( r"[-+]?([0-9]*\.[0-9]+|[0-9]+)" )
        return re_float.findall( self.title )[0]

    @property
    def images_urls( self ):
        try:
            return self._images_urls
        except AttributeError:
            self.load_soup()
            return self._images_urls

    def load_soup( self ):
        page = self.get( self.url )
        raise NotImplementedError
        return page.text

    def enumerate_images_urls( self ):
        for i, url in enumerate( self.images_urls ):
            ext = url.rsplit( '.', 1 )[-1]
            yield "{}.{}".format( i, ext ), url
