from ..config import Configurable
from .column  import Column
from .column  import ColumnManager
from .manager import LibraryManager

import Registry


class Library(Registry, Configurable, parent=Registry):
    @classmethod
    def create_config(cls, parser):
        parser.add_argument('--scan',
                            action  = 'append',
                            default = [],
                            help    = 'Scan the specified library directories and exit')

    @classmethod
    def create(cls, app):
        app.library = LibraryManager(app)

        Registry.Library.Columns.create(app)
        Registry.Library.SearchEngine.create(app)
        Registry.Library.Extensions.create(app)

        if len(app.config.scan) > 0:
            for dirname in app.config.scan:
                dirname = pathlib.Path(dirname).expanduser().absolute()
                app.library.scanDirectory(dirname)
            sys.exit(0)


class SearchEngine(Registry, parent=Library):
    @classmethod
    def create(cls, app):
        # XXX make this user selectable!
        app.search = cls.LogicSearchEngine(app)
        app.search.enable()


class Extensions(Registry, parent=Library):
    @classmethod
    def create(cls, app):
        if not app.config.plugins_disabled:
            if not hasattr(app.columns, '_extensions'):
                app.library._extensions = []

            for plugin in cls.plugins:
                app.library._extensions.append(plugin(app))
                app.library._extensions[-1].enable()


class Columns(Registry, parent=Registry.Library):
    @classmethod
    def create(cls, app):
        app.columns = ColumnManager()

        if not hasattr(app.columns, '_column_defs'):
            app.columns._column_defs = []

        for plugin in cls.plugins:
            app.columns._column_defs.append(plugin(app))
            app.columns._column_defs[-1].enable()


def SummaryDisplay(rec,col='',length=None):
    if length is None:
        if 'length' in rec:
            length = rec['length']
        else:
            length = 0

    def value(key):
        return "" if not key in rec else rec[key]

    form  = f"<font size='3'><b>{value('title')}</b></font> ({round(length//60):d}:{round(length%60):02d})<br/>"
    form += f"<font size='2'>by {value('artist')}</font><br/>"
    form += f"<font size='2'><b>{value('album')}</b></font>"
    if 'tracknumber' in rec:
        if 'albumtracks' in rec:
            numtracks = f" of {rec['albumtracks']}"
        else:
            numtracks = ''
        form += f"<font size='2'> - Track {rec['tracknumber']}{numtracks}</font>"

    return form


class BaseColumns(Registry.Plugin, registry=Registry.Library.Columns):
    standard_columns = [
            Column('mrl',         'Filename', 400, hidden      = True),
            Column('discnumber',  'Disc',      50, displayFunc = lambda r,c: str(r[c]),
                                                   sortFunc    = lambda r,c: f"{r[c]:03d}",
                                                   sortCols    = ['album','discnumber','tracknumber'],
                                                   sortDefault = 0,
                                                   hidden      = True),
            Column('tracknumber', 'Track',     50, displayFunc = lambda r,c: str(r[c]),
                                                   sortFunc    = lambda r,c: f"{r[c]:03d}",
                                                   sortCols    = ['album','discnumber','tracknumber'],
                                                   sortDefault = 0),
            Column('title',       'Title',    200, filterAuto  = True),
            Column('artist',      'Artist',   200, filterAuto  = True,
                                                   sortCols    = ['artist', 'album','discnumber','tracknumber']),
            Column('album',       'Album',    200, filterAuto  = True,
                                                   sortCols    = ['album','discnumber','tracknumber']),
            Column('genre',       'Genre',    200, filterAuto  = True,
                                                   displayFunc = lambda r,c: ', '.join(sorted(r[c])),
                                                   sortFunc    = lambda r,c: ','.join(sorted(r[c])).lower(),
                                                   sortDefault = []),
            Column('year',        'Year',      50, hidden      = True,
                                                   sortFunc    = lambda r,c: f"{r[c]:04d}",
                                                   sortDefault = 0 ),
            Column('length',      'Length',    55, hidden      = True,
                                                   sortFunc    = lambda r,c: f"{int(r[c]//60):05d}:{int(r[c]%60):02d}",
                                                   displayFunc = lambda r,c: f"{int(r[c]//60):d}:{int(r[c]%60):02d}"),
            Column('summary',     'Summary',  100, hidden      = True,
                                                   displayFunc = SummaryDisplay,
                                                   sortFunc    = SummaryDisplay),
            ]

    def enable(self):
        for column in self.standard_columns:
            self.app.columns.add(column)


