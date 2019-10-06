import logging
import pathlib
import urllib

_logger = logging.getLogger(__name__)

class MRLNotImplemented(NotImplementedError): pass
class MRLFileInvalid(IOError): pass

class MRL:
    """Base class representing a generic MRL and all related data"""

    _schemes = {}

    def __init_subclass__(cls, scheme, **kw):
        cls._schemes[scheme] = cls

    def __new__(cls, mrl, **kw):
        if not cls is MRL:
            return super().__new__(cls)

        if mrl is not None:
            # Ensure any filename passed in is converted to an MRL
            mrl = cls._file_to_mrl(mrl)

            # Parse the MRL into its component parts
            parsed = urllib.parse.urlparse(mrl)

            if parsed.scheme in cls._schemes:
                instance = cls._schemes[parsed.scheme].__new__(cls._schemes[parsed.scheme], mrl, **kw)
                return instance
            else:
                raise MRLNotImplemented(f"MRL scheme not implemented: {parsed.scheme}")

        else:
            raise NotImplementedError("OOPS!")

    def __init__(self, mrl):
        self._mrl = self._file_to_mrl(mrl)

    @staticmethod
    def _file_to_mrl(mrl):
        """Detect if the passed in mrl is actually a filename.
        The mrl is converted to a URI if necessary.
        If no conversion is needed, the value is returned unchanged.
        """
        parsed = urllib.parse.urlparse(mrl)
        if parsed.scheme == '':
            path = pathlib.Path(mrl).expanduser().absolute()
            if path.exists():
                mrl = path.as_uri()
                return mrl
            else:
                raise MRLFileInvalid(f"File Not Found: {mrl}")
        else:
            return mrl

    @property
    def mrl(self):
        return self._mrl

    @property
    def scheme(self):
        return urllib.parse.urlparse(self._mrl).scheme

    @property
    def tags(self):
        return {}

class MRLFile(MRL, scheme="file"):
    _coverfiles = ['cover.jpg', 'folder.jpg']
    @property
    def filename(self):
        if self.mrl is None:
            return None
        else:
            return pathlib.Path(urllib.parse.unquote(urllib.parse.urlparse(self.mrl).path))

    def cover(self) -> bytes:
        for cover in self._coverfiles:
            path = self.filename.with_name(cover)
            if path.exists():
                with path.open('rb') as fd:
                    return fd.read()
        return None

