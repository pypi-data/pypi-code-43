import logging as log

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtCore import QAbstractTableModel, QVariant
from PyQt5.QtGui import QFontDatabase


class PropertiesTableModel(QAbstractTableModel):
    HEADERS = [
        QCoreApplication.translate('EventListModel', 'Name'),
        QCoreApplication.translate('EventListModel', 'Value')
    ]


    def __init__(self, element, parent=None):
        """
        :param element: Object of which the properties (__dict__) will be listed
        """
        super().__init__(parent)

        self._dict = None
        if element is not None:
            self._dict = element.__dict__

    def set_item(self, item):
        """
        :type item: Any subclass of element
        """
        self._dict = item.__dict__

    #region## QAbstractTableModel subclassing
    def rowCount(self, parent):
        #pylint: disable=unused-argument
        """ Gives the number of events in the list """
        if self._dict is not None:
            return len(self._dict)
        return 0

    def columnCount(self, parent):
        #pylint: disable=unused-argument, no-self-use
        """ There's 2 columns in the table: Timestamp, Type and Description string"""
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data for the specified cell for the specified role
        :param index: The table cell
        :type index: QModelIndex
        :param role: The Qt role of the returned value (only DisplayRole is implemented)
        """
        row = index.row()
        col = index.column()
        value = QVariant()
        if role in [Qt.DisplayRole, Qt.EditRole]:
            if col == 0:
                value = list(self._dict.keys())[row]
            elif col == 1:
                value = list(self._dict.values())[row]
        elif role == Qt.FontRole:
            font = QFontDatabase.systemFont(QFontDatabase.GeneralFont) #super().data(index, role)
            font.setPointSize(8)
            if col == 0:
                font.setBold(True)
            value = font

        return value

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        #pylint: disable=no-self-use
        """ The table column titles """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return PropertiesTableModel.HEADERS[section]
            return section
        return QVariant()

    ### Edition
    def flags(self, index):
        """ Defines cell properties """
        flags = super().flags(index)
        if index.column() == 1:
            return flags | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        """ Sets data to model """
        #pylint: disable=unused-argument
        key = self.data(self.index(index.row(), 0))
        try:
            data_type = type(self._dict[key])
            self._dict[key] = data_type(value)
            return True
        except TypeError:
            log.error('Data entered "%s" of type "%s" cannot be converted to "%s"',
                      value, type(value), data_type)
            return False
    #endregion##
