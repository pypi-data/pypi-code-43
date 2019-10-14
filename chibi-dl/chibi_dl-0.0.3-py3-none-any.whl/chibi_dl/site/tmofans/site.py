import logging
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from .exceptions import Cannot_pass_cloud_flare, Cannot_login
from .regex import re_show, re_follow, re_pending, re_read
from chibi_dl.site.base.site import Site as Site_base


logger = logging.getLogger( "chibi_dl.sites.tmo_fans" )


class Site( Site_base ):
    def __init__( self, *args, **kw ):
        self._cloud_flare_passed = False
        super().__init__( *args, **kw )

    def build_session( self ):
        self._session = requests.session()

    @property
    def cloud_flare_passed( self ):
        return (
            self._cloud_flare_passed
            or ( self.parent and self.parent.cloud_flared_passed ) )

    @cloud_flare_passed.setter
    def cloud_flare_passed( self, value ):
        self._cloud_flare_passed = value
        if self.parent:
            self.cloud_flare_passed = value

    def cross_cloud_flare( self ):
        if not self.cloud_flare_passed:
            logger.info( "obteniendo {} usando firefox".format( self.url ) )
            self.firefox.get( self.url )
            logger.info( "esperando 10 segundos a que pase cloud flare" )
            time.sleep( 10 )
            self.cookies = self.firefox.get_cookies()
            self.user_agent = self.firefox.execute_script(
                "return navigator.userAgent;" )

            if self.get( self.url ).ok:
                logger.info( "se pueden descargar las imagenes de TMOFans" )
                self.cloud_flare_passed = True
            else:
                raise Cannot_pass_cloud_flare

    @property
    def cookies( self ):
        if self.parent:
            return self.parent.cookies
        try:
            return self._cookies
        except AttributeError:
            return None

    @cookies.setter
    def cookies( self, value ):
        if self.parent:
            self.parent.cookies = value
        else:
            self._cookies = value
            self.session.cookies.clear()
            for cookie in value:
                self.session.cookies.set( cookie[ 'name' ], cookie[ 'value' ] )

    @property
    def firefox( self ):
        if self.parent:
            return self.parent.firefox
        try:
            return self._firefox
        except AttributeError:
            options = Options()
            options.headless = True
            logger.info( "abriendo firefox" )
            self._firefox = webdriver.Firefox( options=options )
            return self._firefox

    def __del__( self ):
        if self.parent is None:
            try:
                self._firefox.quit()
                logger.info( "cerrando firefox" )
            except AttributeError:
                pass
        super().__del__()


class TMO_fans( Site ):
    def __init__( self, *args, user=None, password=None, **kw ):
        super().__init__( 'https://tmofans.com/login', *args, **kw )
        self.series = []
        self.user = user
        self.password = password
        self._login_ok = False

    def append( self, url ):
        from .serie import Serie
        self.cross_cloud_flare()
        if re_show.match( url ):
            self.series.append( Serie( url, parent=self ) )
        elif re_follow.match( url ):
            self.login()
            for l in self.get_all_follow():
                self.append( l )
        elif re_pending.match( url ):
            self.login()
            for l in self.get_all_pending():
                self.append( l )
        elif re_read.match( url ):
            self.login()
            for l in self.get_all_read():
                self.append( l )
        else:
            import pdb
            pdb.set_trace()
            logger.error(
                "la url {} no se pudo identificar como serie".format( url ) )

    def login( self ):
        if self._login_ok:
            return
        if not self.cloud_flare_passed:
            self.cross_cloud_flare()

        page = self.get( self.url )
        soup = BeautifulSoup( page.content, 'html.parser' )
        form = soup.find( "form", { "class": "form-horizontal" } )
        token = form.find( "input", dict( name="_token" ) )[ "value" ]

        payload = dict(
            email=self.user, password=self.password, remember="on",
            _token=token )

        response = self.session.post(
            self.url, data=payload, headers={
                "Referer": self.url,
                "Content-type": "application/x-www-form-urlencoded" } )

        if response.ok and response.url == self.url:
            raise Cannot_login
        else:
            self._login_ok = True

    def get_all_follow( self ):
        page_number = 0
        url = "https://tmofans.com/profile/follow"
        while( True ):
            page_number += 1
            page = self.get( url, params={ "page": page_number } )
            soup = BeautifulSoup( page.content, 'html.parser' )

            links = self.get_manga_links( soup )
            if not links:
                return
            for l in links:
                yield l

    def get_all_pending( self ):
        page_number = 0
        url = "https://tmofans.com/profile/pending"
        while( True ):
            page_number += 1
            page = self.get( url, params={ "page": page_number } )
            soup = BeautifulSoup( page.content, 'html.parser' )

            links = self.get_manga_links( soup )
            if not links:
                return
            for l in links:
                yield l

    def get_all_read( self ):
        page_number = 0
        url = "https://tmofans.com/profile/read"
        while( True ):
            page_number += 1
            page = self.get( url, params={ "page": page_number } )
            soup = BeautifulSoup( page.content, 'html.parser' )

            links = self.get_manga_links( soup )
            if not links:
                return
            for l in links:
                yield l

    def get_manga_links( self, soup ):
        result = []
        for a in soup.find_all( "a" ):
            if "library/" in a[ "href" ]:
                result.append( a[ "href" ].strip() )
        return result

    def i_can_proccess_this( self, url ):
        regex = ( re_show, re_pending, re_read, re_follow )
        return any( ( r.match( url ) for r in regex ) )
