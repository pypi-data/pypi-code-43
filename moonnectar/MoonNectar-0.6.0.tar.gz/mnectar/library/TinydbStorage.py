import bz2
import collections
import datetime
import functools
import json
import lark
import logging
import operator
import pathlib
import re
import shutil
import tinydb
import urllib

from mnectar.action import Action, Actionable
from mnectar.util.signal import Signal

from .abc     import LibraryContent
from .view    import WholeLibrary

_logger = logging.getLogger(__name__)

class LibraryRecordTinyDB(collections.ChainMap):
    def __init__(self, record, parent):
        self.parent = parent
        if isinstance(record, tinydb.database.Document):
            self.__doc_id = record.doc_id
        elif type(record) == int:
            self.__doc_id = record
        elif type(record) == str:
            self.__doc_id = self.parent.bymrl[record].doc_id

        self.__mrl    = self.parent.idMap[self.doc_id]['mrl']
        self.private  = {}

        super().__init__(self.private,
                         self.record['tags'],
                         self.record['meta'],
                         self.record.setdefault('plugin', dict()),
                         {'mrl': self.mrl})

    @property
    def record(self):
        return self.parent.idMap[self.__doc_id]

    @property
    def doc_id(self):
        return self.__doc_id

    @property
    def mrl(self):
        return self.__mrl

    @property
    def filename(self):
        return self._file_uri_to_path(self.mrl)

    def _file_uri_to_path(self, file_uri, path_class=pathlib.PurePath):
        """
        This function returns a pathlib.PurePath object for the supplied file URI.

        :param str file_uri: The file URI ...
        :param class path_class: The type of path in the file_uri. By default it uses
            the system specific path pathlib.PurePath, to force a specific type of path
            pass pathlib.PureWindowsPath or pathlib.PurePosixPath
        :returns: the pathlib.PurePath object
        :rtype: pathlib.PurePath
        """

        # Parse the uri
        file_uri_parsed = urllib.parse.urlparse(file_uri)
        file_uri_path_unquoted = urllib.parse.unquote(file_uri_parsed.path)

        # Verify this is a file uri
        if file_uri_parsed.scheme != 'file':
            raise ValueError("filename conversion is only possible with a 'file://' uri")

        # Check if a windows path was requested, or if it looks like a windows path
        windows_path = isinstance(path_class(),pathlib.PureWindowsPath)
        if not windows_path and re.match('/[A-Za-z]:/', file_uri_path_unquoted):
            windows_path = True

        # Convert windows path
        if windows_path and file_uri_path_unquoted.startswith("/"):
            result = pathlib.PureWindowsPath(file_uri_path_unquoted[1:])

        # Convert posix path
        else:
            result = path_class(file_uri_path_unquoted)

        return result


    def write(self, flush=False):
        self.parent.update(self)
        if flush: self.parent.flush()

    def __copy__(self):
        return type(self)(self.__mrl, self.parent)

    def __deepcopy__(self, memo):
        copy = type(self)(self.__mrl, self.parent)
        memo[id(self)] = copy
        return copy

    def __setitem__(self, item, value):
        if type(item) == str and item.startswith('_'):
            self.private.__setitem__(item, value)
        else:
            self.record['tags'].__setitem__(item, value)

    def __delitem__(self, item):
        if type(item) == str and item.startswith('_'):
            del self.private[item]
        else:
            del self.record[item]

    def __eq__(self, other):
        if type(other) == type(self) and other.doc_id == self.doc_id:
            return True
        elif type(other) == str and other == self.mrl:
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.__mrl,self.__doc_id))

class LibraryContentTinyDB(LibraryContent, Actionable):
    filename = None # Library Content Filename
    idMap    = None # Library content by tinydb doc_id
    mrlMap   = None # Library content by MRL in each document

    sig_updated = Signal()
    sig_deleted = Signal()

    act_backup = Action("Library", "", "Backup Metadata")

    def __init__(self, filename=None, app=None, **kw):
        self.app = app
        super().__init__(**kw)
        if filename is not None:
            self.read(filename)

    @property
    def raw(self):
        """The raw database content"""
        return self.idMap.values()

    @property
    def records(self):
        """Database records wrapped in a utility class"""
        view = WholeLibrary([LibraryRecordTinyDB(_, self) for _ in self.raw], app=self.app)
        self.sig_updated.connect(view.on_inserted_or_updated)
        self.sig_deleted.connect(view.on_deleted)
        return view

    @property
    def ids(self):
        """List of TinyDB record ids"""
        return list(self.idMap.keys())

    @property
    def mrls(self):
        """List of MRL strings accessible contained by this class"""
        return list(self.mrlMap.keys())

    @property
    def tags(self):
        """List of all available tags in the library"""
        return set(_ for record in self.records for _ in record.keys())

    @property
    def query(self):
        """Simplified access to the TinyDB 'Query' functionality"""
        return tinydb.Query()

    @property
    def where(self):
        """Simplified access to the TinyDB 'where' functionality"""
        return tinydb.where

    def read(self, filename):
        """Read database file content"""
        self.filename  = filename
        storage        = tinydb.storages.JSONStorage
        cache          = tinydb.middlewares.CachingMiddleware(storage)
        self.db        = tinydb.TinyDB(self.filename, storage=cache, indent=1)
        self.dbRecords = self.db.table('tracks')
        self.dbConfig  = self.db.table('config')
        self.idMap     = {_.doc_id: _ for _ in self.dbRecords.all()}
        self.mrlMap    = {_['mrl']: _ for _ in self.idMap.values()}

    def update(self, data, cond=None, *, table='tracks'):
        """Insert (if missing) or Update (if found) a record into the database"""
        if isinstance(data, LibraryRecordTinyDB):
            doc = data.record
            if cond is None:
                cond = tinydb.Query().mrl == data.mrl
        elif isinstance(data, collections.abc.Mapping):
            doc = data
        else:
            raise TypeError(f"Invalid Document Data Type: {type(data)}")

        # Perform the update/insert operation
        ids = self.db.table(table).upsert(doc, cond)

        # For each updated/inserted record, update our local cache
        changed = []
        for dbid in ids:
            rec = self.db.table(table).get(doc_id=dbid)
            self.idMap[rec.doc_id] = rec
            self.mrlMap[rec['mrl']] = rec
            changed.append(self[rec.doc_id])

        # Notify that the content has changed.
        if len(changed) > 0:
            self.sig_updated.emit(changed)

    def remove(self, cond, *, table='tracks'):
        # Perform the removal
        ids = self.db.table(table).remove(cond)

        # For each deleted record, remove from the local cache
        deleted = []
        for dbid in ids:
            if dbid in self.idMap:
                deleted.append(self.idMap.pop(dbid))
                self.mrlMap.pop(deleted[-1]['mrl'])

        # Notify the content has been deleted
        if len(deleted) > 0:
            self.sig_deleted.emit(deleted)

    def flush(self):
        self.db.storage.flush()

    def configSave(self, doc, cls):
        # Ensure 'the class name is set in the document
        doc.setdefault('class', cls.__class__.__name__)
        dbConfig = self.db.table('config')
        dbConfig.upsert(doc, tinydb.where('class') == doc['class'])
        self.db.storage.flush()

    def configLoad(self, cls):
        config = self.db.table('config').search(tinydb.where('class') == cls.__class__.__name__)
        if len(config) == 1:
            return config[0]
        elif len(config) > 1:
            _logger.error(f"Multiple '{self.__class__.__name__}' configurations: {config}")
        else:
            return {}

    def __contains__(self, item):
        if isinstance(item, LibraryRecordTinyDB):
            return item.doc_id in self.idMap
        elif type(item) == str:
            return item in self.mrlMap
        elif type(item) == int:
            return item in self.idMap
        elif isinstance(item, collections.abc.Mapping):
            return item in self.raw

    def __iter__(self):
        for recid in self.ids:
            yield LibraryRecordTinyDB(recid, self)

    def __getitem__(self, item):
        if isinstance(item, LibraryRecordTinyDB):
            return  LibraryRecordTinyDB(self.idMap[item.doc_id], self)
        elif type(item) == str:
            return LibraryRecordTinyDB(self.mrlMap[item], self)
        elif type(item) == int:
            return LibraryRecordTinyDB(self.idMap[item], self)
        else:
            raise KeyError(f"Library Content Not Found for Key: {item}")

    def __len__(self):
        return len(self.idMap)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.filename}')"

    def filter(self, query, content=None):
        """Filter the records using a test query function.

        The 'query' function must accept a Mapping object (which will be a database record)
        and return 'True' if the Mapping object should be included in the filter.

        TinyDB provides a powerful query method builder accessible via the 'where' and 'query'
        properties of this class, though any method may be used.
        """
        return [LibraryRecordTinyDB(_, self) for _ in filter(query, self.raw)]

    @act_backup.triggered
    def backup(self):
        current    = pathlib.Path(self.filename)
        suffix     = datetime.datetime.today().strftime(f"{current.suffix}.%Y%m%d_%H%M%S.bz2")
        backupfile = pathlib.Path(self.filename).with_suffix(suffix)

        _logger.info(f"Library Backup: {backupfile}")

        # Create the backup data ...
        serialized = json.dumps(self.db.storage.read(), indent=1)

        # Flush the database to ensure the backup matches existing data
        self.db.storage.flush()

        # Compress the data
        compressed = bz2.compress(serialized.encode('utf-8'))

        with backupfile.open('wb') as fd:
            # Write compressed data to disk
            fd.write(compressed)

