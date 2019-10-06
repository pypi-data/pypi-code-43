import logging

from contextlib                       import contextmanager
from PyQt5.QtCore                     import Qt
from PyQt5                            import QtCore
from PyQt5                            import QtGui
from PyQt5                            import QtWidgets
from mnectar.config                   import Setting
from mnectar.library.view             import Changed, Sorted, Selected
from mnectar.registry                 import Registry, Plugin, PluginSetting
from mnectar.ui.pyqt5.Dockable        import Dockable
from mnectar.ui.pyqt5                 import Action
from mnectar.ui.pyqt5                 import QPlaylistModel
from mnectar.ui.pyqt5                 import HTMLDelegate
from .manager_UI                      import Ui_HashtagManager

import Registry.UI.PyQt

_logger = logging.getLogger(__name__)

class HashtagModel(QtCore.QAbstractTableModel):
    def __init__(self, *arg, records=None, **kw):
        super().__init__(*arg, **kw)
        self.app = self.parent().app

        self.setRecords(records)

    def setRecords(self, records=None):
        self.records = records
        self.refresh()

    @contextmanager
    def _layoutChangeManager(self):
        try:
            # Send a signal that the layout will be changing
            self.layoutAboutToBeChanged.emit([], self.VerticalSortHint)

            # Save the old persistent index list
            # ... so they can be updated later
            old_persist_list = self.persistentIndexList()

            yield
        finally:
            # Create the new persistent index objects

            if len(old_persist_list) > 0:
                invalid = [(_,QtCore.QModelIndex()) for _ in old_persist_list]
                self.changePersistentIndexList([_[0] for _ in invalid], [_[1] for _ in invalid])

            self.layoutChanged.emit([], self.VerticalSortHint)

    def refresh(self):
        with self._layoutChangeManager():
            if self.records is None:
                tags = set(tag
                           for rec in self.app.library.content
                           for tag in rec.get('hashtag', [])
                           )
            else:
                tags = set(tag
                           for rec in self.records
                           for tag in rec.get('hashtag',[])
                           )

            self.hashtags = sorted(tags)

    def rowCount(self, parent=None):
        return len(self.hashtags)

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role, trackStrSort=False):
        if role == QtCore.Qt.DisplayRole:
            return self.hashtags[index.row()]


class HashtagManager(QtWidgets.QWidget, Plugin, Dockable,
                     registry  = Registry.UI.PyQt.Docked,
                     menu      = 'View',
                     menu_name = 'Hashtag Manager',
                     menu_key  = "Ctrl+T",
                     location  = Qt.RightDockWidgetArea):

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self.records = []

        self.config_ui()

    def config_ui(self):
        # Create the UI
        self.ui = Ui_HashtagManager()
        self.ui.setupUi(self)

        # Create the models
        self.model_all     = HashtagModel(self, records=None)
        self.model_current = HashtagModel(self, records=[])

        # Configure the filter proxies
        self.proxy_all = QtCore.QSortFilterProxyModel(self)
        self.proxy_all.setSourceModel(self.model_all)
        self.proxy_all.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_all.setDynamicSortFilter(True)
        self.ui.all.setModel(self.proxy_all)

        self.proxy_current = QtCore.QSortFilterProxyModel(self)
        self.proxy_current.setSourceModel(self.model_current)
        self.proxy_current.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_current.setDynamicSortFilter(True)
        self.ui.current.setModel(self.proxy_current)

        # Setup a link to the selected record tracker
        self.selected_changed = Changed(Sorted(self.app.ui.selected))

        # Setup the selected tracks view
        self.selected_model = QPlaylistModel(app=self.app,
                                             playlist=self.selected_changed, parent=self)

        self.playing_model = QPlaylistModel(
            app=self.app,
            playlist=Changed(Selected(Sorted(self.app.ui.library_view)))
        )

        self.set_selected_model(self.selected_model)

        # Setup signals
        self.ui.entry    .textChanged.connect(self.proxy_all.setFilterFixedString)
        self.ui.entry    .textChanged.connect(self.proxy_current.setFilterFixedString)
        self.ui.refresh  .clicked    .connect(self.model_all.refresh)
        self.ui.add      .clicked    .connect(self.on_add)
        self.ui.remove   .clicked    .connect(self.on_remove)
        self.ui.all      .activated  .connect(self.on_all_tags_activated)
        self.ui.current  .activated  .connect(self.on_current_tags_activated)
        self.ui.playing  .toggled    .connect(self.on_from_playing)
        self.ui.selection.toggled    .connect(self.on_from_selection)

        self.app.signal.playing.connect(self.on_playing)
        self.selected_changed.changed.connect(self.on_selection)

    def set_selected_model(self, model):
        self.ui.selected_view.setModel(model)
        self.ui.selected_view.setModelColumn(self.app.columns.indexOfName('summary'))
        self.ui.selected_view.setItemDelegate(HTMLDelegate())
        self.ui.selected_view.setResizeMode(self.ui.selected_view.Adjust)
        self.ui.selected_view.setSelectionMode(self.ui.selected_view.NoSelection)
        self.ui.selected_view.setAlternatingRowColors(True)

    def on_from_selection(self, state):
        if state:
            self.set_selected_model(self.selected_model)
            self.records = self.selected_model.playlist[:]
            self.update_current_tags()

    def on_from_playing(self, state):
        if state:
            self.set_selected_model(self.playing_model)
            self.records = self.playing_model.playlist[:]
            self.update_current_tags()

    def on_playing(self, pointer, length):
        self.playing_model.playlist.select([pointer.mrl])

        if self.ui.playing.isChecked():
            self.records = [self.app.library.content[pointer.mrl]]
            self.update_current_tags()
            self.ui.selected_title.setTitle(f"Selected: Playing")

    def on_selection(self):
        if self.ui.selection.isChecked():
            content = self.app.library.content
            self.records = [content[_.mrl] for _ in self.app.ui.selected]
            self.update_current_tags()
            self.ui.selected_title.setTitle(f"Selected: {len(self.records)} Records")

    def update_current_tags(self):
        self.model_current.setRecords(self.records)

    def on_add(self, *, tag=None):
        if tag is None:
            tag = self.ui.entry.text()

        modified = False

        for record in self.records:
            if tag not in record.record['plugin'].setdefault('hashtag', list()):
                record.record['plugin']['hashtag'].append(tag)
                record.write(False)
                modified = True

        if modified:
            self.model_current.refresh()
            self.model_all.refresh()
            self.app.library.content.flush()

    def on_remove(self, *, tag=None):
        if tag is None:
            tag = self.ui.entry.text()

        modified = False

        for record in self.records:
            if tag in record.record['plugin'].get('hashtag', list()):
                record.record['plugin']['hashtag'].remove(tag)
                record.write(False)
                modified = True

        if modified:
            self.model_current.refresh()
            self.model_all.refresh()
            self.app.library.content.flush()

    def on_all_tags_activated(self, index):
        if index.isValid():
            tag = self.ui.all.model().data(index, Qt.DisplayRole)
            self.on_add(tag=tag)

    def on_current_tags_activated(self, index):
        if index.isValid():
            tag = self.ui.current.model().data(index, Qt.DisplayRole)
            self.on_remove(tag=tag)
