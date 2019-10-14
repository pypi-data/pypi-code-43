import logging

import ffmpeg
import m3u8
from chibi.atlas import loads
from chibi.file import Chibi_path
from pymkv import MKVFile, MKVTrack

from .exceptions import Cannot_find_subtitles, Episode_not_have_media
from .site import Site
from .subtitles import Subtitle


logger = logging.getLogger( "chibi_dl.sites.crunchyroll.episode" )


class Episode( Site ):
    def __init__( self, url, user, password, *args, **kw ):
        super().__init__( url, *args, user=user, password=password, **kw )

    def download( self, path, download_subtitles=True ):
        logger.info( "inicio de la descarga de subtitulos"  )
        if download_subtitles:
            for subtitles in self.subtitles:
                subtitles.download( path )
        stream = ffmpeg.input( self.stream.uri )
        output_file = path + self.file_name
        stream = ffmpeg.output(
            stream, output_file, loglevel="quiet", codec="copy", )
        logger.info( "inicia la descarga del video '{}' en {}".format(
            self.name, output_file  ) )
        ffmpeg.run( stream )
        return output_file

    def pack( self, path ):
        mkv = MKVFile()
        mkv.add_track( MKVTrack( path + self.file_name, track_id=0 ) )
        mkv.add_track( MKVTrack( path + self.file_name, track_id=1 ) )
        for subtitle in self.subtitles:
            mkv.add_track( subtitle.to_mkv_track( path ) )
        output = path + self.file_name_mkv
        logger.info( "inicia el empaquetado a '{}'".format( self.file_name ) )
        mkv.mux( output, silent=True )
        return output

    @property
    def serie_title( self ):
        title = self.media_metadata.series_title
        title = title.replace( "/", " " )
        return title

    @property
    def number( self ):
        if self.media_metadata.episode_number:
            try:
                return int( self.media_metadata.episode_number )
            except ValueError:
                try:
                    return float( self.media_metadata.episode_number )
                except ValueError:
                    return self.media_metadata.episode_number

    @property
    def title( self ):
        return self.media_metadata.episode_title

    @property
    def name( self ):
        title = self.serie_title.replace( 'Season ', 'S' )
        if self.number:
            return "{serie_title} - {number}".format(
                serie_title=title, number=self.number )
        else:
            return "{serie_title}".format( serie_title=title )

    @property
    def file_name( self ):
        ext = 'm4a'
        result = "{name} {resolution}.{ext}".format(
            name=self.name, ext=ext, resolution=self.resolution_str )
        return Chibi_path( result ).made_safe()

    @property
    def file_name_mkv( self ):
        ext = 'mkv'
        result = "{name} {resolution}.{ext}".format(
            name=self.name, ext=ext, resolution=self.resolution_str )
        return Chibi_path( result ).made_safe()

    @property
    def media_metadata( self ):
        return self.info.config_Config.default_preload.media_metadata

    @property
    def info( self ):
        try:
            return self._info
        except AttributeError:
            self.get_info()
            return self._info

    @property
    def subtitles( self ):
        try:
            return self._subtitles
        except AttributeError:
            self.get_info()
            return self._subtitles

    @property
    def resolution( self ):
        if self.quality == 1080:
            return ( 1920, 1080 )
        elif self.quality == 720:
            return ( 1280, 720 )
        elif self.quality == 480:
            return ( 848, 480 )
        elif self.quality == 360:
            return ( 640, 360 )
        elif self.quality == 240:
            return ( 428, 240 )
        else:
            raise NotImplementedError

    @property
    def resolution_str( self ):
        return "[{}x{}]".format( *self.resolution )

    @property
    def __quality( self ):
        if self.quality == 1080:
            return 80
        elif self.quality == 720:
            return 62
        elif self.quality == 480:
            return 61
        elif self.quality == 360:
            return 60
        elif self.quality == 240:
            return 60
        else:
            raise NotImplementedError

    @property
    def playlist( self ):
        try:
            return self._playlist
        except AttributeError:
            stream_info = self.info.config_Config.default_preload.stream_info
            if 'error' in stream_info:
                raise Episode_not_have_media( stream_info )
            stream_info.file
            straming_list = m3u8.load( stream_info.file )
            self._playlist = straming_list.playlists
            return self._playlist

    @property
    def stream( self ):
        stream_with_my_resolution = filter(
            lambda x: x.stream_info.resolution == self.resolution,
            self.playlist )
        try:
            first_stream = next( stream_with_my_resolution )
        except StopIteration:
            resolutions = [ p.stream_info.resolution for p in self.playlist ]
            logger.exception(
                "no se encontro la resolucion {} resoluciones "
                "encontradas {}".format( self.resolution, resolutions ) )
            raise
        return first_stream

    def get_info( self ):
        media_id = self.url.rsplit( '-', 1 )[1]

        info_url = (
            "http://www.crunchyroll.com/xml/?req=RpcApiVideoPlayer_"
            "GetStandardConfig&media_id={media_id}&video_format=108"
            "&video_quality={quality}&current_page={current_page}"
        ).format(
            media_id=media_id, current_page=self.url,
            quality=self.__quality )
        logger.debug( "descargando informacion del episodio" )
        page = self.get( url=info_url, )

        info = loads( page.text )
        self._info = info
        if 'subtitles' in info.config_Config.default_preload:
            subtitles = info.config_Config.default_preload.subtitles.subtitle
            self.load_subtitles( subtitles )
        else:
            try:
                self.get_info_subtitles()
            except Cannot_find_subtitles:
                self._subtitles = []

    def load_subtitles( self, subtitles ):
        self._subtitles = []
        if isinstance( subtitles, dict ):
            subtitles = [ subtitles ]

        for sub in subtitles:
            self._subtitles.append(
                Subtitle.from_crunchyroll_xml( sub, self ) )

    def get_info_subtitles( self ):
        media_id = self.url.rsplit( '-', 1 )[1]

        info_url = (
            "http://www.crunchyroll.com/xml/?req=RpcApiVideoPlayer_"
            "GetStandardConfig&media_id={media_id}&video_format=108"
            "&video_quality={quality}&current_page={current_page}"
        ).format(
            media_id=media_id, current_page=self.url,
            quality=80 )
        logger.info(
            "descargando informacion del episodio fallback subtitulos" )
        page = self.get( url=info_url, )

        info = loads( page.text )
        if 'subtitles' in info.config_Config.default_preload:
            subtitles = info.config_Config.default_preload.subtitles.subtitle
            self.load_subtitles( subtitles )
        else:
            raise Cannot_find_subtitles
