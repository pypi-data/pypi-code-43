import logging
import re
import shutil

from bs4 import BeautifulSoup
from chibi.file import Chibi_path

from chibi_dl.site.base.site import Site


logger = logging.getLogger( "chibi_dl.sites.tmo_fans.episode" )


class Episode( Site ):
    def download( self, path ):
        logger.info(
            "iniciando la descarga de las {} imagenes del capitulo {}".format(
                len( self.images_urls ), self.number,
            ) )
        for image_name, url in self.enumerate_images_urls():
            image = self.get(
                url, headers={ 'Referer': self.url },
                ignore_status_code=[ 403 ] )
            if not image.ok:
                logger.warning( "no se encontro una imagen" )
                continue
            full_path = path + image_name
            f = full_path.open()
            logger.debug( "descargando {}".format( url ) )
            f.write( image.content )
            logger.debug( "imagen {} guardada".format( f ) )
            image.close()

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
        page = self.get(
            self.url, headers={ "Referer": self.parent.url } )
        cascade = self.get( page.url.replace( 'paginated', "cascade" ) )
        page.close()
        soup = BeautifulSoup( cascade.content, 'html.parser' )
        cascade.close()
        container = soup.find(
            "div", { "class", "viewer-container container" } )
        images = container.find_all( "img" )
        self._images_urls = [ img.get( "src" ) for img in images ]

    def enumerate_images_urls( self ):
        for i, url in enumerate( self.images_urls ):
            ext = url.rsplit( '.', 1 )[-1]
            yield "{}.{}".format( i, ext ), url
