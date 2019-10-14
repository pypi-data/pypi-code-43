import logging

from bs4 import BeautifulSoup
from chibi.file.temp import Chibi_temp_path

from .episode import Episode
from .regex import re_episodes
from .site import Site
from chibi_dl.site.crunchyroll.exceptions import Episode_not_have_media


logger = logging.getLogger( "chibi_dl.sites.crunchyroll.show" )


class Show( Site ):
    def download( self, path ):
        logger.info(
            'iniciando descarga de la serie "{}" de "{}"'.format(
                self.title, self.url ) )
        path += self.title
        path = path.made_safe()
        path.mkdir()
        for episode in self.episodes:
            episode_path = path + episode.file_name_mkv
            if ( episode_path.exists ):
                logger.info( (
                    "ignorando el episodio {} se encontro "
                    "en el destino" ).format( episode.name ) )
                continue
            temp_folder = Chibi_temp_path()
            try:
                episode.download( temp_folder )
            except Episode_not_have_media:
                logger.error( (
                    "el episodio {} no esta disponible posiblemente el "
                    "login no esta correcto" ).format(
                        episode.name ) )
                continue
            mkv = episode.pack( temp_folder )
            mkv.move( path )

    @property
    def title( self ):
        try:
            return self._title
        except AttributeError:
            self.load_episodes()
            return self._title

    @property
    def episodes( self ):
        try:
            return self._episodes
        except AttributeError:
            self.load_episodes()
            return self._episodes

    def load_episodes( self ):
        page = self.get( self.url, )
        soup = BeautifulSoup( page.content, 'html.parser' )
        self._title = soup.select( "h1.ellipsis" )[0].text.strip()

        self._episodes = []
        episodes_links = re_episodes.findall( page.text )
        for episode_link, episode_type in episodes_links:
            episode_link = episode_link.rsplit( '/', 1 )[1]
            episode_url = "{url}/{episode}".format(
                url=self.url, episode=episode_link )
            if episode_link:
                self._episodes.append( Episode.from_site(
                    self, url=episode_url ) )
