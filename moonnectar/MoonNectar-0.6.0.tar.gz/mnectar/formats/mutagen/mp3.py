# ID3 references:
#
#   http://age.hobba.nl/audio/mirroredpages/ID3_comparison.html
#   http://age.hobba.nl/audio/mirroredpages/id3v2.4.0-frames.txt
#   http://age.hobba.nl/audio/tag_frame_reference.html
#   http://id3.org/id3v2.4.0-frames
#   https://en.wikipedia.org/wiki/ID3

import io
import logging
import mutagen
import mutagen.mp3

from dataclasses  import dataclass, field
from typing import Mapping, Any

from .base import MRLFileMutagen

ID3v24Tags = {
    "AENC": {'description': 'Audio encryption',                                 'short' : ''},
    "APIC": {'description': 'Attached picture',                                 'short' : ''},
    "ASPI": {'description': 'Audio seek point index',                           'short' : ''},
    "COMM": {'description': 'Comments',                                         'short' : ''},
    "COMR": {'description': 'Commercial frame',                                 'short' : ''},
    "ENCR": {'description': 'Encryption method registration',                   'short' : ''},
    "EQU2": {'description': 'Equalization',                                     'short' : ''},
    "ETCO": {'description': 'Event timing codes',                               'short' : ''},
    "GEOB": {'description': 'General encapsulated object',                      'short' : ''},
    "GRID": {'description': 'Group identification registration',                'short' : ''},
    "LINK": {'description': 'Linked information',                               'short' : ''},
    "MCDI": {'description': 'Music CD identifier',                              'short' : ''},
    "MLLT": {'description': 'MPEG location lookup table',                       'short' : ''},
    "OWNE": {'description': 'Ownership frame',                                  'short' : ''},
    "PCNT": {'description': 'Play counter',                                     'short' : ''},
    "POPM": {'description': 'Popularimeter',                                    'short' : ''},
    "POSS": {'description': 'Position synchronisation frame',                   'short' : ''},
    "PRIV": {'description': 'Private frame',                                    'short' : ''},
    "RBUF": {'description': 'Recommended buffer size',                          'short' : ''},
    "RVA2": {'description': 'Relative volume adjustment',                       'short' : ''},
    "RVRB": {'description': 'Reverb',                                           'short' : ''},
    "SEEK": {'description': 'Seek frame',                                       'short' : ''},
    "SIGN": {'description': 'Signature frame',                                  'short' : ''},
    "SYLT": {'description': 'Synchronized lyric/text',                          'short' : ''},
    "SYTC": {'description': 'Synchronized tempo codes',                         'short' : ''},
    "TALB": {'description': 'Album/Movie/Show title',                           'short' : 'album'},
    "TBPM": {'description': 'Beats per minute (BPM)',                           'short' : 'bpm'},
    "TCOM": {'description': 'Composer',                                         'short' : 'composer'},
    "TCON": {'description': 'Content type',                                     'short' : 'genre'},
    "TCOP": {'description': 'Copyright message',                                'short' : 'copyright'},
    "TDEN": {'description': 'Encoding time',                                    'short' : ''},
    "TDLY": {'description': 'Playlist delay',                                   'short' : ''},
    "TDOR": {'description': 'Original release year',                            'short' : ''},
    "TDRC": {'description': 'Date',                                             'short' : 'date'},
    "TDRL": {'description': 'Release Date',                                     'short' : 'releasedate'},
    "TDTG": {'description': 'Tagging time',                                     'short' : ''},
    "TENC": {'description': 'Encoded by',                                       'short' : 'encodedby'},
    "TEXT": {'description': 'Lyricist/Text writer',                             'short' : 'lyricist'},
    "TFLT": {'description': 'File type',                                        'short' : ''},
    "TIPL": {'description': 'Involved people list',                             'short' : ''},
    "TIT1": {'description': 'Content group description',                        'short' : 'grouping'},
    "TIT2": {'description': 'Title/songname/content description',               'short' : 'title'},
    "TIT3": {'description': 'Subtitle/Description refinement',                  'short' : 'version'},
    "TKEY": {'description': 'Initial key',                                      'short' : ''},
    "TLAN": {'description': 'Language(s)',                                      'short' : ''},
    "TLEN": {'description': 'Length',                                           'short' : ''},
    "TMCL": {'description': 'Musician credits list',                            'short' : ''},
    "TMED": {'description': 'Media type',                                       'short' : ''},
    "TMOO": {'description': 'Mood',                                             'short' : 'mood'},
    "TOAL": {'description': 'Original album/movie/show title',                  'short' : ''},
    "TOFN": {'description': 'Original filename',                                'short' : ''},
    "TOLY": {'description': 'Original lyricist(s)/text writer(s)',              'short' : ''},
    "TOPE": {'description': 'Original artist(s)/performer(s)',                  'short' : ''},
    "TOWN": {'description': 'File owner/licensee',                              'short' : ''},
    "TPE1": {'description': 'Lead performer(s)/Soloist(s)',                     'short' : 'artist'},
    "TPE2": {'description': 'Band/orchestra/accompaniment',                     'short' : ''},
    "TPE3": {'description': 'Conductor/performer refinement',                   'short' : ''},
    "TPE4": {'description': 'Interpreted, remixed, or otherwise modified by',   'short' : 'arranger'},
    "TPOS": {'description': 'Part of a set',                                    'short' : 'discnumber'},
    "TPRO": {'description': 'Produced notice',                                  'short' : ''},
    "TPUB": {'description': 'Publisher',                                        'short' : 'publisher'},
    "TRCK": {'description': 'Track number/Position in set',                     'short' : 'tracknumber'},
    "TRSN": {'description': 'Internet radio station name',                      'short' : ''},
    "TRSO": {'description': 'Internet radio station owner',                     'short' : ''},
    "TSOA": {'description': 'Album sort order',                                 'short' : 'albumsort'},
    "TSOP": {'description': 'Performer sort order',                             'short' : 'artistsort'},
    "TSOT": {'description': 'Title sort order',                                 'short' : 'titlesort'},
    "TSRC": {'description': 'International Standard Recording Code (ISRC)',     'short' : 'isrc'},
    "TSSE": {'description': 'Software/Hardware and settings used for encoding', 'short' : ''},
    "TSST": {'description': 'Set subtitle',                                     'short' : 'discsubtitle'},
    "TXXX": {'description': 'User defined text information frame',              'short' : ''},
    "UFID": {'description': 'Unique file identifier',                           'short' : ''},
    "USER": {'description': 'Terms of use',                                     'short' : ''},
    "USLT": {'description': 'Unsynchronized lyric/text transcription',          'short' : ''},
    "WCOM": {'description': 'Commercial information',                           'short' : ''},
    "WCOP": {'description': 'Copyright/Legal information',                      'short' : ''},
    "WOAF": {'description': 'Official audio file webpage',                      'short' : ''},
    "WOAR": {'description': 'Official artist/performer webpage',                'short' : ''},
    "WOAS": {'description': 'Official audio source webpage',                    'short' : ''},
    "WORS": {'description': 'Official internet radio station homepage',         'short' : ''},
    "WPAY": {'description': 'Payment',                                          'short' : ''},
    "WPUB": {'description': 'Publishers official webpage',                      'short' : ''},
    "WXXX": {'description': 'User defined URL link frame',                      'short' : ''},
}
ID3v24TagsReverse = {info['short']:tag for tag,info in ID3v24Tags.items() if info['short']}

@dataclass
class MP3TagMap:
    apptag: str             # Application tag name
    mp3tag: str             # MP3 tag name or 'info' (must set "info" value as well)
    onget:  callable = None # Callable which modifies the value when getting this tag
    onset:  callable = None # Callable which modifies the value when setting this tag (NONE: Not setable)
    dbdoc:  bool     = True # Include this tag when generating a database document for the file
    select: callable = None # Select function to choose between multiple versions of the same tag
    info:   str      = None # file 'info' value (not valid with mp3tag)

    def get(self, tags):
        # Determine if this is a recursive call ...
        if type(tags) == mutagen.id3.ID3:
            # Look for an exact mutagen tag match ...
            if self.mp3tag in tags:
                tag = tags[self.mp3tag]

            # If the above all fail, look for a delimited mutagen tag
            elif len(self.mp3tag) == 4:
                mtags = (_ for _ in tags.keys() if _.startswith(self.mp3tag))
                tag = tuple(tags[_] for _ in mtags)
            else:
                tag = tuple()

            # Detect empty tag list
            if type(tag) is tuple and len(tag) == 0:
                raise KeyError(f'Tag {self.mp3tag} does not exist!')

            # Run the delimited tag select function if defined
            if type(tag) == tuple and self.select is not None:
                # Normal callable object
                if callable(self.select):
                    tag = self.select(tag)
                # Static methods might require special handling
                # ... if configured during class creation
                elif hasattr(self.select, '__func__'):
                    tag = self.select.__func__(tag)

            # Recursively call this method to extract tag data
            if type(tag) == tuple:
                return tuple(self.get(_) for _ in tag)
        elif isinstance(tags, mutagen.id3.Frame):
            tag = tags
        else:
            raise ValueError("Unable to parse input")

        # Extract the value from a mutagen tag object
        if isinstance(tag, mutagen.id3.NumericTextFrame):
            value = int(tag.text[0].lstrip())

        elif isinstance(tag, mutagen.id3.NumericPartTextFrame):
            if '/' in tag.text[0]:
                value = tuple(int(_.lstrip('0')) for _ in tag.text[0].split('/'))
            else:
                value = (int(tag.text[0].lstrip('0')), None)

        elif isinstance(tag, mutagen.id3.TimeStampTextFrame):
            value = tuple((_.year, _.month, _.day, _.hour, _.minute, _.second) for _ in tag.text if _.year is not None)

        elif isinstance(tag, mutagen.id3.TextFrame):
            # Fix broken encodings as necessary (cached)
            self._recode_latin1(tag)

            if len(tag.text) == 1:
                value = tag.text[0]
            else:
                value = tuple(tag.text)

        elif isinstance(tag, mutagen.id3.APIC):
            return tag.data

        else:
            raise NotImplementedError(f"Attempt to retrieve unsupported tag [{self.mp3tag}] of type {type(tag)}: {tag}")

        if type(value) in (tuple,list) and len(value) == 0 or value is None:
            return None
        elif callable(self.onget):
            return self.onget(value)
        else:
            return value
        return tags

    def _recode_latin1(self, tag: mutagen.id3.TextFrame) -> mutagen.id3.TextFrame:
        """
        MP3 tags often have an encoding listed as Latin1 when in fact they are UTF-8.
        This method will attempt to recode Latin1 encoded strings as UTF-8 to fix this
        error.
        """
        # This branch is designed to be called recursively!
        # ... it should only becalled with a utf-8 string that was not properly labeled
        # ... Exceptions must be checked for to determine success of the encoding!
        if type(tag) == str:
            return tag.encode('iso-8859-1').decode('utf-8')

        elif type(tag) == list:
            return [self._recode_latin1(_) for _ in tag]

        elif type(tag) == tuple:
            return tuple(self._recode_latin1(_) for _ in tag)

        elif isinstance(tag, mutagen.id3.Frame) and hasattr(tag, 'text') and tag.encoding == mutagen.id3._specs.Encoding.LATIN1:
            try:
                recoded = self._recode_latin1(tag.text)
                if type(recoded) == str:
                    tag.text = recoded
                    tag.encoding = mutagen.id3._specs.Encoding.UTF8
                elif type(recoded) == list:
                    for _ in range(len(recoded)):
                        tag.text[_] = recoded[_]
                    tag.encoding = mutagen.id3._specs.Encoding.UTF8

                return tag

            except UnicodeError:
                pass
            except LookupError:
                pass
        else:
            return tag

class MRLFileMutagenMP3(MRLFileMutagen, ftype=mutagen.mp3.MP3):

    @staticmethod
    def _get_cover(tags):
        types = {_.type:_ for _ in tags}

        # In the official mp3 spec, 3 is the cover
        # ... however not all embedded cover iamges honor this
        # ... try to get type 3 (cover)
        # ... then type 0 (the most likely default value)
        # ... then whatever is first in the list
        if 3 in types:
            return types[3]
        elif 0 in types:
            return types[0]
        else:
            return tags[0]

    _mp3_tags = [
        MP3TagMap('album',         'TALB', ),
        MP3TagMap('albumsort',     'TSOA', ),
        MP3TagMap('albumdiscs',    'TPOS', lambda _:_[1]),
        MP3TagMap('albumtracks',   'TRCK', lambda _:_[1]),
        MP3TagMap('arranger',      'TPE4', ),
        MP3TagMap('artist',        'TPE1', ),
        MP3TagMap('artistsort',    'TSOP', ),
        MP3TagMap('bpm',           'TBPM', ),
        MP3TagMap('composer',      'TCOM', ),
        MP3TagMap('copyright',     'TCOP', ),
        MP3TagMap('year',          'TDRC', lambda _:_[0][0]),
        MP3TagMap('discnumber',    'TPOS', lambda _:_[0]),
        MP3TagMap('discsubtitle',  'TSST', ),
        MP3TagMap('genre',         'TCON', lambda _:[_] if type(_) == str else _),
        MP3TagMap('grouping',      'TIT1', ),
        MP3TagMap('isrc',          'TSRC', ),
        MP3TagMap('lyricist',      'TEXT', ),
        MP3TagMap('mood',          'TMOO', ),
        MP3TagMap('publisher',     'TPUB', ),
        MP3TagMap('title',         'TIT2', ),
        MP3TagMap('titlesort',     'TSOT', ),
        MP3TagMap('tracknumber',   'TRCK', lambda _:_[0]),
        MP3TagMap('version',       'TIT3', ),
        MP3TagMap('cover',         'APIC', select=_get_cover, dbdoc=False),
    ]

    _tdict = {_.apptag:_ for _ in _mp3_tags}

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        if self.mrl is not None:
            self._mtags = mutagen.File(self.filename)

    @property
    def info(self):
        return self._mtags.info

    def __getitem__(self, key):
        # Look for an application tag
        if key in self._tdict:
            return self._tdict[key].get(self._mtags.tags)

        # Look for an exact mutagen tag match ...
        elif key in self._mtags.tags:
            return self._mtags.tags[key]

        # If the above all fail, look for a delimited mutagen tag
        elif len(key) == 4 and key.isupper():
            mtags = (_ for _ in self._mtags.tags.keys() if _.startswith(key))
            values = tuple(self._mtags.tags[_] for _ in mtags)

            if len(values) > 0:
                return values

        # No value found, raise an exception
        raise KeyError(f"Tag {key} does not exist")

    def tags(self):
        """Mutagen raw tag list (undelimited)"""
        return set(_.split(':')[0] for _ in self._mtags.tags.keys())

    def __iter__(self):
        filekeys = self._mtags.tags.keys()
        filetags = [_[:4] for _ in filekeys]
        for apptag,tagdef in self._tdict.items():
            if apptag in filetags:
                yield apptag

    def __contains__(self, key):
        return key in self.keys()

    def keys(self):
        filekeys = self._mtags.tags.keys()
        filetags = [_[:4] for _ in filekeys]
        apptags  = [_ for _ in self._tdict.keys() if self._tdict[_].mp3tag in filetags]
        return set(filekeys).union(apptags)

    def appkeys(self):
        filekeys = self._mtags.tags.keys()
        filetags = [_[:4] for _ in filekeys]
        apptags  = [_ for _ in self._tdict.keys() if self._tdict[_].mp3tag in filetags]
        return apptags

    def appitems(self):
        for key in self.appkeys():
            yield key,self[key]

    def dbdoc(self):
        return {
                'mrl': self.mrl,
                'tags': { key:val for key,val in self.appitems() if self._tdict[key].dbdoc and val is not None},
                'meta': {
                    'length': self._mtags.info.length,
                    'format': self._mtags.mime[0].split('/')[1],
                    'cover': 'cover' in self
                    },
                }

    def cover(self):
        try:
            cover = self['cover']
        except KeyError:
            cover = super().cover()
        return cover

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.mrl}')"

