import logging

from .exceptions import Cannot_login
from .regex import re_show, re_video, re_lenguage, re_csrf_token
from chibi_dl.site.base.site import Site as Site_base


logger = logging.getLogger( "chibi_dl.sites.crunchyroll" )


class Site( Site_base ):
    @property
    def token( self ):
        if self.parent:
            return self.parent.token
        return self._token

    @token.setter
    def token( self, value ):
        if self.parent:
            self.parent._token = value
        self._token = value

    @property
    def cookie( self ):
        if self.parent:
            return self.parent.cookie
        return self._cookie

    @cookie.setter
    def cookie( self, value ):
        if self.parent:
            self.parent._cookie = value
        self._cookie = value

    def _pre_to_dict( self ):
        return dict(
            url=self.url, user=self.user, password=self.password,
            lenguage=self.lenguage, quality=self.quality )


class Crunchyroll( Site ):
    def __init__( self, *args, **kw ):
        super().__init__( '', *args, **kw )
        self.series = []

    def append( self, url ):
        from .serie import Show
        lenguage = re_lenguage.search( url )
        if not lenguage:
            logger.error(
                "no se encontro el lenguaje en la url {}".format( url ) )
        lenguage = lenguage.group( 1 )
        self.lenguage = lenguage

        if re_show.match( url ):
            self.series.append( Show(
                url, user=self.user, password=self.password, parent=self,
                lenguage=lenguage, quality=self.quality ) )
        elif re_video.match( self.url ):
            raise NotImplementedError
        else:
            logger.error( "no se pudo identificar el tipo de la url" )

    def login( self ):
        login_url = "https://www.crunchyroll.com/{country}/login".format(
            country=self.lenguage )

        headers = {
            'Referer': login_url,
        }

        logger.info( "intentanto logearse" )

        initial_page_fetch = self.get( url=login_url, headers=headers )

        if initial_page_fetch.status_code == 200:
            initial_cookies = self.session.cookies
            csrf_token = re_csrf_token.search(
                initial_page_fetch.text ).group( 1 )

            payload = {
                'login_form[name]': self.user,
                'login_form[password]': self.password,
                'login_form[redirect_url]': '/',
                'login_form[_token]': csrf_token,
            }

            self.session.post(
                url=login_url, data=payload, headers=headers,
                cookies=initial_cookies)

            logger.info( "termino de logerase" )
            """
            response = self.get(
                url=self.url, headers=headers,
                cookies=initial_cookies )
            """
            self.cookie = initial_cookies
            self.token = csrf_token
            self.session.cookies = self.cookie
            self.session.headers.update( {
                'Upgrade-Insecure-Requests': '1',
                'Accept-Encoding': 'gzip, deflate'
            } )
        else:
            raise Cannot_login(
                "no se pudo conectar a la pagina de loging",
                status_code=initial_page_fetch.status_code )

    def i_can_proccess_this( self, url ):
        return re_show.match( url )
