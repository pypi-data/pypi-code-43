#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys

from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex

PY_DATE_FORMAT = "%Y-%m-%d %a"
PY_TIME_FORMAT = "%H:%M"


class AdvertsTableModel(QAbstractTableModel):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data               # DON'T CALL THIS ATTRIBUTE "data", A QAbstractItemModel METHOD ALREADY HAVE THIS NAME (model.data(index, role)) !!!

    def rowCount(self, parent):
        return self._data.num_rows

    def columnCount(self, parent):
        return self._data.num_columns

    def data(self, index, role):

        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self._data.get_data(index.row(), index.column())

            if value is not None:
                if role == Qt.DisplayRole and self._data.dtype[index.column()] == datetime.date:
                    value = value.strftime(format=PY_DATE_FORMAT)
                elif role == Qt.DisplayRole and self._data.dtype[index.column()] == datetime.time:
                    value = value.strftime(format=PY_TIME_FORMAT)

            return value

        return QVariant()    # For others roles...

    def headerData(self, index, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return str(index+1)
            elif orientation == Qt.Horizontal:
                return self._data.headers[index]
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            try:
                row_index, column_index = index.row(), index.column()

                #if self._data.dtype[column_index] == datetime.datetime:
                #    value = datetime.datetime.strptime(value, PY_DATE_TIME_FORMAT)
                if self._data.dtype[column_index] == float:
                    value = float(value)                      # Expect numerical values here... remove otherwise

                self._data.set_data(row_index, column_index, value)
            except Exception as e:
                print(e, file=sys.stderr)
                return False

            # The following lines are necessary e.g. to dynamically update the QSortFilterProxyModel
            # "When reimplementing the setData() function, dataChanged signal must be emitted explicitly"
            # http://doc.qt.io/qt-5/qabstractitemmodel.html#setData
            # TODO: check whether this is the "right" way to use the dataChanged signal

            self.dataChanged.emit(index, index, [Qt.EditRole])

        return True

    def flags(self, index):
        """Returns the item flags for the given `index`.

        See Also
        --------
        - http://doc.qt.io/qt-5/qabstractitemmodel.html#flags
        - http://doc.qt.io/qt-5/qt.html#ItemFlag-enum

        Parameters
        ----------
        index : QModelIndex
            TODO

        Returns
        -------
        ItemFlags
            The item flags for the given `index`.
        """
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def insertRows(self, row, count, parent):
        """Inserts `count` rows into the model before the given `row`.

        Items in the new row will be children of the item represented by the `parent` model index.

        If `row` is 0, the rows are prepended to any existing rows in the `parent`.

        If `row` is `rowCount()`, the rows are appended to any existing rows in the `parent`.

        If `parent` has no children, a single column with `count` rows is inserted.

        Returns `True` if the rows were successfully inserted; otherwise returns `False`.

        See Also
        --------
        http://doc.qt.io/qt-5/qabstractitemmodel.html#insertRows

        Parameters
        ----------
        row : int
            TODO
        count : int
            TODO
        parent : QModelIndex, optional
            TODO

        Returns
        -------
        bool
            Returns `True` if the rows were successfully removed; otherwise returns `False`.
        """
        try:
            parent = parent
            first_index = row
            last_index = first_index + count - 1

            self.beginInsertRows(parent, first_index, last_index)

            for i in range(count):
                self._data.insert_row(first_index)

            self.endInsertRows()
        except Exception as e:
            print(e)
            return False

        return True

    def removeRows(self, row, count, parent):
        """Removes `count` rows starting with the given `row` under parent `parent` from the model.

        See Also
        --------
        http://doc.qt.io/qt-5/qabstractitemmodel.html#removeRows

        Parameters
        ----------
        row : int
            TODO
        count : int
            TODO
        parent : QModelIndex, optional
            TODO

        Returns
        -------
        bool
            Returns `True` if the rows were successfully removed; otherwise returns `False`.
        """
        # See http://doc.qt.io/qt-5/qabstractitemmodel.html#removeRows

        try:
            parent = parent
            first_index = row
            last_index = first_index + count - 1

            self.beginRemoveRows(parent, first_index, last_index)

            for i in range(count):
                self._data.remove_row(first_index)

            self.endRemoveRows()
        except Exception as e:
            print(e, file=sys.stderr)
            return False

        return True


    @property
    def dtype(self):
        return self._data.dtype
