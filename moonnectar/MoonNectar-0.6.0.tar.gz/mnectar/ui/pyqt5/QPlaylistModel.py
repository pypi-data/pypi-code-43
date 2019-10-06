import logging
import pathlib
import urllib

from contextlib   import contextmanager
from PyQt5        import QtCore
from PyQt5        import QtGui
from PyQt5.QtCore import Qt

from mnectar.library.view import Sorted, Filtered, Changed

from .roles import UserRoles

_logger = logging.getLogger(__name__)

class QPlaylistModel(QtCore.QAbstractTableModel):
    _playing  = None
    _playlist = None

    #playIndexChanged = QtCore.pyqtSignal(object,object) # Linked to playlist signal

    def __init__(self, app=None, playlist=None, *arg, **kw):
        super().__init__(*arg, **kw)
        self.app = app

        if playlist is None:
            self.playlist = Changed(Sorted(Filtered(self.app.library.content.records, self.app)))
            self.playlist.changed.connect(self.on_columns_changed)
        else:
            self.playlist = playlist

            # Connect the changed signal if it exists
            if isinstance(playlist, Changed):
                self.playlist.changed.connect(self.on_columns_changed)

        self.app.columns.changed.connect(self.on_columns_changed)
        self.app.signal.playing.connect(self.on_playing)

        #TODO: Decide how default sorting should be handled!
        self.sort(0)

    def on_columns_changed(self, *arg):
        # This is a brute force solution
        # ... rather than detect what was changed
        # ... reset the entire model in any change
        # ... this is slow and bad programming
        # ... but ultimately the easiest solution give the external data source
        # ... TODO: Make this more elegant if performance becomes an issue!
        self.modelReset.emit()

    def on_playing(self, pointer, length):
        # XXX Revisit This!!!!
        if pointer.view == self.playlist:
            if self._playing is None:
                old = None
            elif self._playing.view_index == -1:
                old = None
            else:
                old = self._playing.view_index

            self._playing = pointer

            if self._playing.view_index < 0:
                new = None
            else:
                new = self._playing.view_index

            self.on_play_index_changed(old, new)
        else:
            if self._playing is None:
                old = None
            elif self._playing.view_index is None:
                old = None
            elif self._playing.view_index < 0:
                old = None
            else:
                old = self._playing.view_index

            if old is not None:
                self.on_play_index_changed(old, None)

            self._playing = None

    @property
    def active(self):
        return self._playing is not None and self._playing.view == self.playlist

    @property
    def playing_index(self):
        if self.active:
            return self._playing.view_index
        else:
            return None

    @property
    def playlist(self):
        return self._playlist

    @playlist.setter
    def playlist(self, value):
        # Disconnect old signals
        if self._playlist is not None:
            #self._playlist.playIndexChanged.disconnect(self.on_play_index_changed)
            #self._playlist.changed.disconnect(self.on_playlist_changed)
            pass

        self._playlist = value

        # Convert python playlist signals to pyqt signals
        #self._playlist.playIndexChanged.connect(self.on_play_index_changed)
        #self._playlist.changed.connect(self.on_playlist_changed)

    @contextmanager
    def _layoutChangeManager(self):
        try:
            # Send a signal that the layout will be changing
            self.layoutAboutToBeChanged.emit([], self.VerticalSortHint)

            # Save the old persistent index list
            # ... so they can be updated later
            old_persist_list = self.persistentIndexList()
            old_index_rows = [x.row() for x in old_persist_list]
            old_index_records = [self.playlist[x] for x in old_index_rows]

            for record,index in zip(old_index_records, old_persist_list):
                if not '_persist' in record:
                    record['_persist'] = []
                record['_persist'].append(index)

            yield
        finally:
            # Create the new persistent index objects

            if len(old_persist_list) > 0:
                playlist_enumerated = enumerate(self.playlist)
                persist_list_map    = list(filter(lambda _: '_persist' in _[1], playlist_enumerated))
                missing             = old_persist_list.copy()
                complete            = []

                # An empty persist list map means new playlist content
                # ... this should only happen when loading content from the library
                # ... and means all existing persistent indexes can be recreated by searching for records
                # XXX NOTE: This may fail if filtering a playlist with duplicate entries!
                if len(persist_list_map) == 0:
                    new_index_list = []
                    for old_rec,old_index in zip(old_index_records,old_persist_list):
                        try:
                            new_row = self.playlist.index(old_rec)
                            new_index_list.append(self.index(new_row, old_index.column(), old_index.parent()))
                        except ValueError:
                            new_index_list.append(QtCore.QModelIndex())
                    self.changePersistentIndexList(old_persist_list, new_index_list)

                # A persist list map that is non-empty means in-place sort/filter/insert/delete
                # ... update indexes as possible
                # ... and mark all others as invalid
                else:
                    # Build a list of persistent indexes that still exist
                    for row,record in persist_list_map:
                        for index in record['_persist']:
                            ito = self.index(row, index.column(), index.parent())
                            complete.append((index, self.index(row, index.column(), index.parent())))
                        del record['_persist']

                    complete_orig = [_[0] for _ in complete]
                    invalid       = filter(lambda _: _ not in complete_orig, missing)
                    invalid_map   = [(_,QtCore.QModelIndex()) for _ in invalid]
                    complete.extend(invalid_map)

                    self.changePersistentIndexList([_[0] for _ in complete], [_[1] for _ in complete])

            self.layoutChanged.emit([], self.VerticalSortHint)

    def sort(self, column=None, order=Qt.AscendingOrder):
        with self._layoutChangeManager():
            if column is None:
                self.playlist.sort(None, order != Qt.AscendingOrder)
            else:
                self.playlist.sort(self.app.columns[column].name, order != Qt.AscendingOrder)

    def playIndex(self, index):
        if index.isValid():
            self.app.signal.playNew.emit(self.playlist.pointer(index.row()))

    def filter(self, filterstr=None):
        with self._layoutChangeManager():
            self.playlist.filter(filterstr)

    def get_mrl(self, row):
        try:
            return self.playlist[row].mrl
        except IndexError:
            return None

    def index_of_mrl(self, mrl):
        return self.playlist.index(mrl)

    def on_play_index_changed(self, old, new):
        if old is not None:
            change_from_index = [self.createIndex(old, 0),
                                 self.createIndex(old, len(self.app.columns)-1),
                                 [QtCore.Qt.BackgroundRole]*len(self.app.columns)]
            self.dataChanged.emit(*change_from_index)

        if new is not None:
            change_to_index   = [self.createIndex(new, 0),
                                 self.createIndex(new, len(self.app.columns)-1),
                                 [QtCore.Qt.BackgroundRole]*len(self.app.columns)]
            self.dataChanged.emit(*change_to_index)

    def rowCount(self, parent=None):
        return len(self.playlist)

    def columnCount(self, parent=None):
        return len(self.app.columns)

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | super().flags(index)
        else:
            return super().flags(index)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self.app.columns[section].description

    def data(self, index, role, trackStrSort=False):
        if role == QtCore.Qt.DisplayRole:
            try:
                record = self.playlist[index.row()]
                column = self.app.columns[index.column()].name
                if trackStrSort:
                    value = self.app.columns[index.column()].sortFunc(record, column)
                else:
                    value = self.app.columns[index.column()].displayFunc(record, column)
                return value
            except KeyError as ex:
                return ""

        elif role == QtCore.Qt.BackgroundRole:
            if self.active and index.row() == self.playing_index:
                return QtGui.QColor(QtGui.QColor(150,150,200))

        elif role == QtCore.Qt.ToolTipRole:
            return self.data(index, QtCore.Qt.DisplayRole)

        elif role == UserRoles.AlbumSortByAlbum.value:
            indicies = [self.index(index.row(), self.app.columns.indexOfName(col)) for col in ['album', 'tracknumber']]
            return '#'.join([str(self.data(idx, Qt.DisplayRole, trackStrSort=True)) for idx in indicies])

        elif role == UserRoles.AlbumSortByArtist.value:
            indicies = [self.index(index.row(), self.app.columns.indexOfName(col)) for col in ['artist', 'album', 'tracknumber']]
            return '#'.join([str(self.data(idx, Qt.DisplayRole, trackStrSort=True)) for idx in indicies])

        elif role == UserRoles.AlbumSortByTrack.value:
            indicies = [self.index(index.row(), self.app.columns.indexOfName(col)) for col in ['album', 'tracknumber']]
            return '#'.join([str(self.data(idx, Qt.DisplayRole, trackStrSort=True)) for idx in indicies])

    def insertRows(self, row, count, parent):
        return super().insertRows(row, count, parent)

    def insertRow(self, row, count, parent):
        return super().insertRow(row, parent)

    def setData(self, index, role):
        super().setData(index, role)

    def dropMimeData(self, data, action, row, column, parent):
        if 'text/uri-list' in data.formats():
            # NOTE:  QUrl tries to be helpful by default, prett-printing urls.
            #        ... this produces a questionably valid url
            #        ... this breaks library lookups by mrl
            #        ... and the url will normally never be looked at by a human!
            #        Solution:  Always decode the url using the 'FullyEncoded' formatting option
            mrls = [_.url(_.FullyEncoded) for _ in data.urls()]
            m3u = [_ for _ in mrls if _.endswith('.m3u') and _.startswith('file:')]

            if len(m3u) > 0 and len(m3u) != len(mrls):
                raise NotImplementedError("Mixed m3u and file mime drops are not yet implemented!")

            elif len(m3u) > 0:
                with self._layoutChangeManager():
                    parsed = [urllib.parse.urlparse(_) for _ in m3u]
                    paths  = [pathlib.Path(urllib.parse.unquote(_.path)) for _ in parsed if _.scheme == 'file']
                    for path in paths:
                        if path.exists():
                            with path.open(encoding='utf-8') as fd:
                                ix=0
                                for line in fd:
                                    # Strip off whitespace including the newline character
                                    line = line.strip()

                                    # Get the actual filename
                                    if line.startswith('#'):
                                        continue
                                    elif line.startswith('/'):
                                        filename = pathlib.Path(line)
                                    elif line.startswith('./'):
                                        filename = path.parent/line[2:]
                                    else:
                                        filename = path.parent/line

                                    # Attempt to add the filename to the playlist
                                    try:
                                        mrl = filename.as_uri()
                                        record = self.app.library.content[mrl]
                                        if row == -1 and not parent.isValid():
                                            self.playlist.append(record)
                                        elif parent.isValid():
                                            self.playlist.insert(parent.row()+1+ix, record)
                                        else:
                                            self.playlist.insert(row+ix, record)
                                        ix+=1
                                    except KeyError:
                                        _logger.debug(f"M3U entry not found in library: {filename.as_uri()}")
                return True

            elif action in (Qt.CopyAction, Qt.MoveAction):
                with self._layoutChangeManager():
                    for ix,mrl in enumerate(mrls):
                        try:
                            _logger.debug3(f"COPY: @{row}+{parent.row()}+{ix}: {mrl}")
                            record = self.app.library.content[mrl]
                            if row == -1 and not parent.isValid():
                                self.playlist.append(record)
                            elif parent.isValid():
                                self.playlist.insert(parent.row()+1+ix, record)
                            else:
                                self.playlist.insert(row+ix,record)
                        except KeyError:
                            _logger.debug(f"Ignoring invalid MRL: {mrl}")
                            return False
                return True
        return False

    def mimeData(self, indexes):
        rows = list({_.row():0 for _ in indexes})
        mrls = [QtCore.QUrl(self.playlist[_]['mrl']) for _ in rows]
        data = QtCore.QMimeData()
        data.setUrls(mrls)
        return data

    def mimeTypes(self):
        return ['text/uri-list']

    def removeRows(self, row, count, parent):
        with self._layoutChangeManager():
            for _ in range(count):
                self.playlist.pop(row)
        return True

    def removeRow(self, row, parent):
        with self._layoutChangeManager():
            self.playlist.pop(row)
        return True

