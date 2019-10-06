import logging

from enum         import Enum, unique
from weakref      import finalize
from PyQt5        import QtCore
from PyQt5        import QtGui
from PyQt5        import QtWidgets
from PyQt5.QtCore import Qt

from mnectar.config import Setting

from .action import Action

_logger = logging.getLogger(__name__)

class QPlaylistView(QtWidgets.QTableView):
    """A PyQt5 view customized for display of a music playlist"""

    CAN_DRAG   = True
    CAN_DROP   = False
    CAN_DELETE = False

    savedState = Setting(default=None)
    _name      = 'Unknown'

    def __init_subclass__(cls, can_drag = None, can_drop = None, can_delete = None, **kw):
        super().__init_subclass__(**kw)

        if can_drag   is not None: cls.CAN_DRAG   = can_drag
        if can_drop   is not None: cls.CAN_DROP   = can_drop
        if can_delete is not None: cls.CAN_DELETE = can_delete

    def __init__(self, *arg, can_drag = None, can_drop = None, can_delete = None, **kw):
        super().__init__(*arg, **kw)

        if can_drag   is not None: self.CAN_DRAG   = can_drag
        if can_drop   is not None: self.CAN_DROP   = can_drop
        if can_delete is not None: self.CAN_DELETE = can_delete

        self.config_ui()
        self.config_actions()
        self.config_signal()

        finalize(self, self.on_close)

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def sizeHintForColumn(self, column):
        return self.window().app.columns[column].sizeHint

    def on_close(self):
        # Saving the state with no playlist causes errors and is also pointless
        if getattr(self.model(), 'playlist', None) is not None:
            _logger.debug(f"Close Event ... saving playlist view: {self.name()}")
            self.savedState = self.saveState()

    def saveState(self):
        header = self.horizontalHeader()
        return {
            'columns': [
                {
                    'visualIndex':  col,
                    'logicalIndex': header.logicalIndex(col),
                    'hidden':       header.isSectionHidden(header.logicalIndex(col)),
                    'size':         header.sectionSize(header.logicalIndex(col)),
                    'name':         header.model().headerData(col, Qt.Horizontal, Qt.DisplayRole),
                }

                for col in range(header.count())
            ],

            'sortIndicatorShown':   header.isSortIndicatorShown(),
            'sortIndicatorSection': header.sortIndicatorSection(),
            'sortIndicatorOrder':   header.sortIndicatorOrder(),
        }

    def restoreState(self, state):
        if state is not None:
            header = self.horizontalHeader()

            header.setSortIndicatorShown(state['sortIndicatorShown'])

            if state['sortIndicatorShown']:
                header.setSortIndicator(state['sortIndicatorSection'], state['sortIndicatorOrder'])

            for column in state['columns']:
                vi = column['visualIndex']
                li = column['logicalIndex']

                if li > len(self.window().app.columns):
                    _logger.debug2(f"Column does not exist (removed?) at index [{li}]: '{column['name']}'")
                    continue

                if vi != li:
                    _logger.error("Column Reorder Not Supported")
                    break

                name = header.model().headerData(li, Qt.Horizontal, Qt.DisplayRole)

                if name != column['name']:
                    _logger.error(f"Column name mismatch '{name}' != '{column['name']}'")
                    continue

                header.setSectionHidden(li, column['hidden'])
                header.resizeSection(li, column['size'])


    def config_ui(self):
        """Configure the widget"""

        if self.CAN_DRAG and self.CAN_DROP:
            dragDropMode = self.DragDrop
            dropAction   = Qt.MoveAction
        elif self.CAN_DRAG:
            dragDropMode = self.DragOnly
            dropAction   = Qt.IgnoreAction
        elif self.CAN_DROP:
            dragDropMode = self.DropOnly
            dropAction   = Qt.CopyAction
        else:
            dragDropMode = self.NoDragDrop
            dropAction   = Qt.IgnoreAction

        self.verticalHeader().setVisible(False)         # No left-side header
        self.setSortingEnabled(True)                    # Sorting is enabled
        self.setSelectionBehavior(self.SelectRows)      # Select entire rows at a time (not cells)
        self.setContextMenuPolicy(Qt.CustomContextMenu) # Enable right-click context menu
        self.setAlternatingRowColors(True)              # Alternating row colors
        self.setWordWrap(False)                         # Do not wrap words (tooltips are used instead)
        self.setDragDropOverwriteMode(False)            # Drop will always insert, never overwrite!
        self.setDragEnabled(self.CAN_DRAG)              # drag source?
        self.setAcceptDrops(self.CAN_DROP)              # Drop destination?
        self.viewport().setAcceptDrops(self.CAN_DROP)   # Drop destination?
        self.setDropIndicatorShown(self.CAN_DROP)       # Show the drop indicator?
        self.setDragDropMode(dragDropMode)              # Set the drag/drop mode
        self.setDefaultDropAction(dropAction)           # Action on drop
        self.setStyle(_DropRowStyle())                  # Style Override: Entire Row drop indicator

        self.horizontalHeader().show()                                     # Show the horizontal (top) header
        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu) # Enable context menu on the header

    def config_signal(self):
        """Configure signals for the widget"""
        self.activated.connect(self.on_activated)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.horizontalHeader().customContextMenuRequested.connect(self.on_header_context_menu)
        self.window().app.signal.playing.connect(self.on_playing)

    def config_actions(self):
        if self.CAN_DELETE:
            self.addAction(Action("Delete Selected Tracks", self, shortcut=Qt.Key_Backspace, onTriggered=self.on_delete))

    def setModel(self, model):
        super().setModel(model)
        # Resize the columns to contents (or default sizes)
        # ... These are default widths
        # ... Set here because column names and widths come from the model
        self.resizeColumnsToContents()

        # Set default hidden columns
        # ... this happens before restoring any saved state
        # ... as saved states take precedence!
        for column in self.window().app.columns.index(hidden=True):
            self.setColumnHidden(column, True)

        # Some header configuration must happen after the model has been set
        self.horizontalHeader().setSectionsMovable(True)      # Columns can be moved via drag/drop
        self.restoreState(self.savedState) # Restore the table layout

    def on_context_menu(self, pos):
        menu = QtWidgets.QMenu()
        for action in self.actions():
            menu.addAction(action)
        self.get_context_menu_actions(menu)
        action = menu.exec_(self.mapToGlobal(pos))

    def on_header_context_menu(self, pos):
        menu = QtWidgets.QMenu()

        def getcb(col):
            def func(show):
                self.setColumnHidden(col, not show)
                if show:
                    self.resizeColumnToContents(col)
            return func

        for idx,column in enumerate(self.window().app.columns.values()):
            menu.addAction(Action(column.description, menu,
                checkable   = True,
                checked     = not self.isColumnHidden(idx),
                onTriggered = getcb(idx)))

        action = menu.exec_(self.mapToGlobal(pos))

    def get_context_menu_actions(self, menu):
        for action in self.actions():
            menu.addAction(action)

    def selectedRows(self):
        return set(_.row() for _ in self.selectedIndexes())

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        mrls = [self.model().get_mrl(_) for _ in self.selectedRows()]
        self.window().app.ui.selected.select(mrls)
        self.window().app.signal.pyqt.selected.emit(mrls)

    def on_delete(self, *arg, **kw):
        # Remove rows in reverse order so that indexes do not change during deletion
        rows = reversed(sorted(self.selectedRows()))
        result = [self.model().removeRow(_, QtCore.QModelIndex()) for _ in rows]

    def get_vindex_from_mrl(self, mrl):
        # FIXME: This will fail with duplicate playlist entries!

        playlist_index = self.model().index_of_mrl(mrl)
        if playlist_index is None:
            return QtCore.QModelIndex()
        else:
            mindex = self.model().index(playlist_index, 0)
            return mindex

    def on_activated(self, vindex):
        self.model().playIndex(vindex)

    def on_playing(self, pointer, length):
        if pointer.view == self.model().playlist:
            index = pointer.view_index
            if index is not None:
                # NOTE: Qt has strange behavior where scrollTo fails to work unless the
                # first column is visible.  So if that column is visible, it must be
                # unhidden before scrolling.  Simply selecting a different unhidden
                # column is NOT sufficient!

                header = self.horizontalHeader()
                hidden = header.isSectionHidden(header.logicalIndex(0))
                qidx = self.model().index(index, 0)

                if hidden:
                    self.setColumnHidden(0, False)

                self.scrollTo(self.model().index(index, 0), self.EnsureVisible)

                if hidden:
                    self.setColumnHidden(0, True)

class _DropRowStyle(QtWidgets.QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Draw a line across the entire row rather than just the column we're hovering over.
        NOTE: This may not always work depending on global style or operating system
        """
        if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
            option_new = QtWidgets.QStyleOption(option)
            option_new.rect.setLeft(0)
            if widget:
                option_new.rect.setRight(widget.width())
            option = option_new
        super().drawPrimitive(element, option, painter, widget)

