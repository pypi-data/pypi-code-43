from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import QVariant

from .list import ListModel
from .data.screenshot import Screenshot


class SnapList(QObject):
    """
    Class managing a collection of user input events.
    All items in the list of events must subclass Event
    """
    list_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.snaps = []

    def push(self, item):
        if isinstance(item, Screenshot):
            self.snaps.append(item)
            self.list_changed.emit()

    def get(self, index):
        if index < len(self.snaps):
            return self.snaps[index]
        return None

    def size(self):
        return len(self.snaps)

    def get_serializable(self):
        """ :return: this object as a dict """
        return {
            'screenshots': list(map(lambda l: l.__dict__, self.snaps))
        }

    @pyqtSlot(Screenshot)
    def remove(self, snap):
        if snap in self.snaps:
            self.snaps.remove(snap)
            self.list_changed.emit()
            return True
        return False

    @pyqtSlot()
    def clear(self):
        """ Removes all the elements from the list """
        del self.snaps[:]
        self.list_changed.emit()


class SnapListModel(ListModel):
    """ Model for displaying an SnapList in a QListView """

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data for the specified cell for the specified role
        :param index: The table cell
        :type index: QModelIndex
        :param role: The Qt role of the returned value (only DisplayRole is implemented)
        """
        if role == Qt.DisplayRole:
            item = self._data.get(index.row())
            return str('Snapshot: x={0} y={1} size={2}x{3}'.format(item.x, item.y, item.w, item.h))

        return QVariant()
