from chibi_dl.site.crunchyroll import Crunchyroll
from chibi_dl.site.tmofans import TMO_fans


class Site:
    def __init__( self, user, password, **kw ):
        self.crunchytoll = Crunchyroll( user=user, password=password, **kw )
        self.tmo_fans = TMO_fans( user=user, password=password, **kw )
        self._sites = [ self.crunchytoll, self.tmo_fans ]

    def append( self, *urls ):
        for url in urls:
            site = self.identify_site( url )
            site.append( url )

    def identify_site( self, url ):
        for site in self._sites:
            if site.i_can_proccess_this( url ):
                return site

    def download( self, path ):
        if self.crunchytoll.series:
            self.crunchytoll.login()

        for serie in self.crunchytoll.series:
            serie.download( path )

        for serie in self.tmo_fans.series:
            serie.download( path )

    def print( self, only_links ):
        if self.crunchytoll.series:
            self.crunchytoll.login()

        if only_links:
            self.print_links()
            return

        for serie in self.crunchytoll.series:
            print( serie.name, len( serie.episodes ), serie.url )
            for episode in serie.episodes:
                print( "\t", episode.name, episode.title )

        for serie in self.tmo_fans.series:
            print( serie.name, len( serie.episodes ), serie.url )

    def print_links( self ):
        for serie in self.crunchytoll.series:
            print( serie.url )

        for serie in self.tmo_fans.series:
            print( serie.url )
