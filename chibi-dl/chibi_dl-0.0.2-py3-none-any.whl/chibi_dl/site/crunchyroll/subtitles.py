import base64
import logging
import zlib

import pycountry
from chibi.atlas import loads
from chibi.parser import to_bool
from pymkv import MKVTrack

from .external.aes import aes_cbc_decrypt
from .external.utils import obfuscate_key, bytes_to_intlist, intlist_to_bytes
from .site import Site


logger = logging.getLogger( "chibi_dl.sites.crunchyroll.subtitle" )


class Subtitle( Site ):
    def __init__( self, url, user, password, *args, **kw ):
        self._default = kw.pop( 'default' )
        super().__init__( url, *args, user=user, password=password, **kw )

    @classmethod
    def from_crunchyroll_xml( cls, d, episode ):
        try:
            d[ 'url' ] = d[ 'link' ]
            del d[ 'link' ]
            return cls.from_site( site=episode, **d )
        except Exception as e:
            import pdb
            pdb.set_trace()

    def get_info( self ):
        logger.debug( "obteniendo info del subtitulo" )
        page = self.get( self.url )
        data = loads( page.text ).subtitle
        page.close()
        self.id = data.id
        self._data = loads( self.decrypt_subtitles( data.data, data.iv ) )
        self._data = self.data.subtitle_script

    @property
    def default( self ):
        return to_bool( self._default )

    @property
    def data( self ):
        try:
            return self._data
        except AttributeError:
            self.get_info()
            return self._data

    @property
    def lang( self ):
        return "{}-{}".format(
            self.data.lang_code[:2], self.data.lang_code[-2:] )

    @property
    def lang_ISO_639_2( self ):
        try:
            return pycountry.languages.get(
                alpha_2=self.lang[:2] ).bibliographic
        except AttributeError:
            return pycountry.languages.get( alpha_2=self.lang[:2] ).alpha_3

    @property
    def name( self ):
        return "{name}.{lang}".format(
            name=self.parent.name, lang=self.lang, ext='ass' )

    @property
    def file_name( self ):
        ext = 'ass'
        return "{name}.{ext}".format( name=self.name, ext=ext )

    def download( self, path ):
        output_path = path + self.file_name
        f = output_path.open()
        f.write( self.to_ass() )
        logger.info( "descargado subtitulo '{}' ".format( f ) )
        return output_path

    def to_mkv_track( self, path ):
        track = MKVTrack(
            path + self.file_name, language=self.lang_ISO_639_2,
            default_track=self.default, track_name=self.data.title )
        return track

    def to_ass( self ):
        output = ''

        def ass_bool(strvalue):
            assvalue = '0'
            if strvalue == '1':
                assvalue = '-1'
            return assvalue

        output = '[Script Info]\n'
        output += 'Title: %s\n' % self.data.title
        output += 'ScriptType: v4.00+\n'
        output += 'WrapStyle: %s\n' % self.data['wrap_style']
        output += 'PlayResX: %s\n' % self.data['play_res_x']
        output += 'PlayResY: %s\n' % self.data['play_res_y']
        output += "[V4+ Styles]\n"
        output += (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour,"
            " OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,"
            " ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow,"
            " Alignment, MarginL, MarginR, MarginV, Encoding" )
        if not isinstance( self.data.styles.style, list ):
            self.data.styles.style = [ self.data.styles.style ]
        for style in self.data.styles.style:
            output += 'Style: ' + style['name']
            output += ',' + style['font_name']
            output += ',' + style['font_size']
            output += ',' + style['primary_colour']
            output += ',' + style['secondary_colour']
            output += ',' + style['outline_colour']
            output += ',' + style['back_colour']
            output += ',' + ass_bool(style['bold'])
            output += ',' + ass_bool(style['italic'])
            output += ',' + ass_bool(style['underline'])
            output += ',' + ass_bool(style['strikeout'])
            output += ',' + style['scale_x']
            output += ',' + style['scale_y']
            output += ',' + style['spacing']
            output += ',' + style['angle']
            output += ',' + style['border_style']
            output += ',' + style['outline']
            output += ',' + style['shadow']
            output += ',' + style['alignment']
            output += ',' + style['margin_l']
            output += ',' + style['margin_r']
            output += ',' + style['margin_v']
            output += ',' + style['encoding']
            output += '\n'

        output += """
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        if not isinstance( self.data.events.event, list ):
            self.data.events.event = [ self.data.events.event ]
        for event in self.data.events.event:
            output += 'Dialogue: 0'
            output += ',' + event['start']
            output += ',' + event['end']
            output += ',' + event['style']
            output += ',' + event['name']
            output += ',' + event['margin_l']
            output += ',' + event['margin_r']
            output += ',' + event['margin_v']
            output += ',' + event['effect']
            output += ',' + event['text']
            output += '\n'

        return output

    def decrypt_subtitles( self, data, iv ):
        data = bytes_to_intlist( base64.b64decode( data ) )
        iv = bytes_to_intlist( base64.b64decode( iv ) )
        id = int( self.id )
        key = obfuscate_key( id )
        decrypted_data = intlist_to_bytes(
            aes_cbc_decrypt( data, key, iv ) )
        return zlib.decompress( decrypted_data )
