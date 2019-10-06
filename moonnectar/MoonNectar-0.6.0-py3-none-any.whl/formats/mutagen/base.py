import logging
import pathlib
import urllib
import mutagen

from mnectar.formats import MRLFile
from mnectar.formats import MRLNotImplemented, MRLFileInvalid

_logger = logging.getLogger(__name__)

class MRLFileMutagen(MRLFile, scheme="file"):
    _ftypes = {}

    def __new__(cls, mrl, **kw):
        if not cls is MRLFileMutagen:
            return object.__new__(cls)

        mfile = pathlib.Path(urllib.parse.unquote(urllib.parse.urlparse(mrl).path))

        try:
            mtag = mutagen.File(mfile)
            ftype = type(mtag)

            if mtag is None:
                raise MRLFileInvalid(f"Not a mutagen parseable file type: '{mfile}'")
            elif ftype not in cls._ftypes:
                raise MRLNotImplemented(f"Mutagen type not implemented: {ftype}")
            else:
                instance = cls._ftypes[ftype].__new__(cls._ftypes[ftype], mrl, **kw)
                return instance
        except mutagen.MutagenError as ex:
            raise MRLFileInvalid(ex)

    def __init_subclass__(cls, ftype, **kw):
        cls._ftypes[ftype] = cls

    def __init__(self, mrl, **kw):
        super().__init__(mrl, **kw)

        try:
            self._mtags = mutagen.File(self.filename)
            if self._mtags is None:
                raise TypeError(f"MRL is not readable by mutagen: '{self.mrl}'")
        except mutagen.MutagenError:
            raise TypeError(f"MRL is not readable by mutagen: '{self.mrl}'")


