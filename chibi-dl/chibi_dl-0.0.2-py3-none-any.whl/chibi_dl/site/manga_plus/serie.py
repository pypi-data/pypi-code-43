import logging

from chibi.request import Chibi_url

from .episode import Episode
from .regex import re_chapter, re_chapter_title, re_title
from chibi_dl.site.base.site import Site


logger = logging.getLogger( "chibi_dl.sites.manga_plus.serie" )


class Serie( Site ):
    def __init__( self, url, *args, **kw ):
        url = Chibi_url( url )
        api_url = Chibi_url(
            "https://jumpg-webapi.tokyo-cdn.com/api/title_detail" )
        api_url = api_url + { 'title_id': url.base_name }
        url = api_url
        super().__init__( url, *args, **kw )

    def download( self, path ):
        raise NotImplementedError

    @property
    def name( self ):
        try:
            return self._title
        except AttributeError:
            self.load_soup()
            return self._title

    @property
    def episodes( self ):
        try:
            return self._episodes
        except AttributeError:
            self.load_soup()
            return self._episodes

    def load_soup( self ):
        page = self.get( self.url, )
        page.close()
        chapters = re_chapter.findall( page.text )
        chapters_titles = re_chapter_title.findall( page.text )
        title = re_title.findall( page.text )
        if title:
            title = title[0].strip()

        # url_base = "https://mangaplus.shueisha.co.jp/viewer/{id}"
        url_base = Chibi_url(
            "https://jumpg-webapi.tokyo-cdn.com/api/manga_viewer" )
        params = { 'chapter_id': "", 'split': "yes", 'img_quality': 'high' }

        self._episodes = []
        for chapter_id, chapter_title in zip( chapters, chapters_titles ):
            params[ "chapter_id" ] = chapter_id
            self._episodes.append( Episode.from_site(
                site=self, url=url_base + params,
                title=chapter_title ) )
