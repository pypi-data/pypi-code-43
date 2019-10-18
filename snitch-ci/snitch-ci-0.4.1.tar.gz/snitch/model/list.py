"""
Package containing classes derived from QObjects defining models handling events
"""
import logging as log

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QAbstractTableModel, QVariant, QModelIndex


class ListModel(QAbstractTableModel):
    """ Base class for TableModels handling lists """

    def __init__(self, data, parent=None):
        """
        :type data: EventList
        """
        super().__init__(parent)

        self._data = data
        self._last_size = data.size()

        self._data.list_changed.connect(self.update_list)
        self._last_col = 0

    #region## QAbstractTableModel subclassing
    def rowCount(self, parent):
        #pylint: disable=unused-argument
        """ Gives the number of events in the list """
        return self._data.size()

    def columnCount(self, parent):
        #pylint: disable=unused-argument, no-self-use
        return 1

    def data(self, index, role=Qt.DisplayRole):
        #pylint: disable=unused-argument, no-self-use
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        #pylint: disable=unused-argument, no-self-use
        return QVariant()
    #endregion##

    def update_list(self):
        """ Handles data list change """
        size = self._data.size()
        last_row = size-1

        if size > self._last_size:
            log.debug('Inserting %d -> %d', self._last_size, size)
            self.beginInsertRows(QModelIndex(), self._last_size, last_row)
            self.endInsertRows()
        elif size < self._last_size:
            log.debug('Removing %d -> %d', self._last_size, size)
            self.beginRemoveRows(QModelIndex(), last_row+1, self._last_size-1)
            self.endRemoveRows()

        self.dataChanged.emit(self.index(0, 0), self.index(last_row, self._last_col))
        self._last_size = size
