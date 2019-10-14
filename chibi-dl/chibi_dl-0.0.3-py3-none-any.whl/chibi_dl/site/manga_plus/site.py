import logging

from .regex import re_show
from chibi_dl.site.base.site import Site as Site_base


logger = logging.getLogger( "chibi_dl.sites.manga_plus" )


class Site( Site_base ):
    pass


class Manga_plus( Site ):
    def __init__( self, *args, **kw ):
        super().__init__(
            'https://mangaplus.shueisha.co.jp/updates', *args, **kw )
        self.series = []

    def append( self, url ):
        from .serie import Serie
        if re_show.match( url ):
            self.series.append( Serie( url, parent=self ) )
        else:
            logger.error(
                "la url {} no se pudo identificar como serie".format( url ) )

    def i_can_proccess_this( self, url ):
        regex = ( re_show, )
        return any( ( r.match( url ) for r in regex ) )
