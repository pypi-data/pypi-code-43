import logging
import os
import pathlib
import tinydb
import tinydb.middlewares
import urllib

from ..util.signal  import Signal
from ..config       import Configurable
from ..config       import Setting
from ..formats      import MRL
from ..vars         import __appname__
from .column        import Column
from .TinydbStorage import LibraryContentTinyDB

_logger = logging.getLogger(__name__)


class LibraryManager(Configurable):
    _default_covers   = ['cover.jpg', 'folder.jpg']
    _default_dbfile   = pathlib.Path.home()/f".{__appname__}/library.json"
    content           = None
    app               = None

    libraryChanged    = Signal()
    libraryDirAdded   = Signal()
    libraryDirRemoved = Signal()

    directories   = Setting('library.directories',   None, None, default=list,            help="Music Directories")
    dbfile        = Setting('library.dbfile',        None, None, default=_default_dbfile, help="Library Database File")
    scan_at_start = Setting('library.scan_at_start', None, None, default=False,           help="Scan Music Directories at Startup")
    cover_files   = Setting('library.cover_files',   None, None, default=_default_covers, help="Album Art Filenames")

    @classmethod
    def create_config(cls, parser):
        """Create the application configuration"""
        parser.add_argument('-D', '--database',  action = 'store', dest='database_file', help = "Specify the library database file")

    def __init__(self, app=None, filename=None, **kw):
        self.app      = self.app or app
        self.filename = filename

        super().__init__(**kw)

        self.dbLoad()

    def dbLoad(self, filename=None):

        if filename is not None:
            self.filename = filename
        elif self.app.config.database_file is not None:
            self.filename = self.app.config.database_file
        elif self.filename is None:
            return

        self.filename = pathlib.Path(self.filename).expanduser().absolute()

        _logger.debug(f"Opening Library Database: {self.filename}")

        self.content = LibraryContentTinyDB(self.filename, app=self.app)
        self._configLoad()

    def _config(self):
        return {'directories': self.directories}

    def _configSave(self):
        self.content.configSave(self._config(), self)

    def _configLoad(self):
        config = self.content.configLoad(self)

        for path in config.get('directories',[]):
            self.addDirectory(path,save=False)

    def addDirectory(self, directory, save=True):
        # NOTE:  If loading the configuration from the database via '_configLoad()',
        #        ... set: save=False
        #        ... this avoids overwriting the database with empty content!
        #        XXX Is there a better way?

        # NOTE: Convert the directory to a string object as pathlib is not
        #       always fully supported and is of minimal use going forward.
        directory = str(directory)

        if not directory in self.directories:
            self.directories.append(directory)
            self.libraryDirAdded.emit(directory)

            if save:
                self._configSave()

    def removeDirectory(self,directory):
        if directory is self.directories:
            self.directories.remove(directory)
            self.libraryDirRemoved.emit(directory)
            self._configSave()

    def reload(self):
        """Reload the track list from the database (not the entire file)"""
        self.content.read(self.filename)

        #XXX REMOVE ME??
        #XXX Or Update Me??
        #self.libraryChanged.emit()

    def scanFile(self, filename, flush=True):
        try:
            track = tinydb.Query()
            taginfo = MRL(filename)
            _logger.debug3(f"Scanning File: {filename}")

            self.content.update(taginfo.dbdoc(), track.mrl == taginfo.mrl)
        except IOError:
            _logger.debug3(f"Invalid Audio File: {filename}")
        except NotImplementedError:
            _logger.debug2(f"Format Not Implemented: {filename}")

        # By default, ensure any new database data is written to disk (flush)
        # ... but that can be overridden for directly level scanning
        if flush:
            self.content.flush()

    def scanDirectory(self, directory):
        directory = pathlib.Path(directory).expanduser().absolute()
        _logger.debug(f"Scanning Directory: {directory}")
        for root, dirs, files in os.walk(directory, followlinks=True):
            for filename in files:
                # Ignore dot files!
                if filename[0] != '.':
                    path = os.path.join(root, filename)
                    self.scanFile(path, flush=False)

        self.addDirectory(directory, save=False)

        # Ensure all data is written to disk!
        self.content.flush()

        # Reload the database
        self.reload()

    def moveFile(self, src_mrl, dst_mrl):
        src_mrl = pathlib.Path(src_mrl).as_uri()
        dst_mrl = pathlib.Path(dst_mrl).as_uri()

        if src_mrl in self.content:
            _logger.debug(f"File Moved: [{src_mrl}] => [{dst_mrl}]")
            self.content.update({'mrl':dst_mrl}, tinydb.Query().mrl == src_mrl)
            self.content.flush()
            self.reload()
        else:
            _logger.debug(f"File Move Ignored: [{src_mrl}] => [{dst_mrl}]")

    def deleteFile(self, filename):
        mrl = pathlib.Path(filename).as_uri()
        if mrl in self.content:
            _logger.debug(f"File Delete: {mrl}")
            self.content.remove(tinydb.Query().mrl == mrl)
            self.content.flush()
        else:
            _logger.debug(f"File Delete Ignored: {mrl}")

    def filter(self, string=""):
        """Filter the loaded database content using the provided search string"""
        return self.content.filter(string)

