import logging

from PyQt5.QtCore         import Qt
from PyQt5                import QtCore
from PyQt5                import QtWidgets
from mnectar.config       import Setting
from mnectar.ui.pyqt5     import Dockable
from mnectar.ui.pyqt5     import QPlaylistModel
from mnectar.ui.pyqt5     import QPlaylistView
from mnectar.ui.pyqt5     import Action
from mnectar.library.view import Sorted, Filtered, Changed, Editable

import Registry.UI.PyQt

_logger = logging.getLogger("mnectar."+__name__)


class QueueModel(QPlaylistModel):
    delete_after_play = Setting(default=True)

    _to_delete = None

    def __init__(self, app=None, *arg, **kw):
        playlist = Changed(Sorted(Filtered(Editable([], app))))
        super().__init__(app=app, playlist=playlist, *arg, **kw)

        self.app.signal.playEnd    .connect(self.on_play_end)
        self.app.signal.playing    .connect(self.on_do_delete)
        self.app.signal.playlistEnd.connect(self.on_do_delete)

    def on_play_end(self, pointer):
        if pointer.view == self.playlist:
            self._to_delete = pointer

    def on_do_delete(self, *arg, **kw):
        if self.delete_after_play and self._to_delete is not None:
            if self._to_delete.valid:
                self.removeRow(self._to_delete.view_index, QtCore.QModelIndex())
            self._to_delete = None

    def filter(self, filterstr=None):
        # Filtering is ignored
        super().filter(None)

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | super().flags(index)
        else:
            return super().flags(index) | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def supportedDragActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def dropMimeData(self, data, action, row, column, parent):
        try:
            if len(self.playlist) == 0:
                _sig_play_after = True
            else:
                _sig_play_after = False

            return super().dropMimeData(data, action, row, column, parent)

        finally:
            if _sig_play_after:
                self.app.signal.playAfter.emit(self.playlist.pointer(0))

class Queue(QPlaylistView, Dockable, Registry.Plugin,
            registry   = Registry.UI.PyQt.Docked,
            menu       = 'View',
            menu_name  = 'Queue',
            menu_key   = "Ctrl+L",
            location   = Qt.BottomDockWidgetArea,
            can_drag   = True,
            can_drop   = True,
            can_delete = True):

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

    def config_ui(self):
        super().config_ui()
        self._model = QueueModel(app=self.app)

        self.setName('Queue')
        self.setModel(self._model)

        self.app.signal.playing.connect(self.on_playing)

    def on_playing(self, pointer, length):
        if pointer.view != self.model().playlist and len(self.model().playlist) > 0:
            self.app.signal.playAfter.emit(self.model().playlist.pointer(0))

    def get_context_menu_actions(self, menu):
        super().get_context_menu_actions(menu)

        menu.addAction(Action("Delete After Playback", menu,
            checkable = True,
            checked   = self.model().delete_after_play,
            onToggled = lambda _: setattr(self.model(), 'delete_after_play', _)))

        #XXX FIXME XXX FIXME XXX FIXME
        #menu.addAction(Action("Activate Previous Playlist on Empty Queue", menu,
            #checkable = True,
            #checked   = self.model().playlist.activatePreviousPlaylistOnEmpty,
            #onToggled = lambda _: setattr(self.model().playlist, 'activatePreviousPlaylistOnEmpty', _)))
