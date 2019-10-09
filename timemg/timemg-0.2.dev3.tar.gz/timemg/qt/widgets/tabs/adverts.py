#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PyQt5.QtWidgets import QTableView, QWidget, QPushButton, QVBoxLayout, QAbstractItemView, \
    QAction, QPlainTextEdit, QLineEdit, QHBoxLayout

from timemg.qt.delegates.adverts import AdvertsTableDelegate
from timemg.qt.models.adverts import AdvertsTableModel

class AdvertsTab(QWidget):

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)

        self.tabs = parent

        # Make widgets ####################################

        self.table_view = QTableView(parent=self)
        self.btn_add_row = QPushButton("Add a row", parent=self)

        # Set layouts #####################################

        vbox = QVBoxLayout()
        vbox.addWidget(self.table_view)
        vbox.addWidget(self.btn_add_row)
        self.setLayout(vbox)

        # Set model #######################################

        adverts_model = AdvertsTableModel(data, parent=self)  # TODO: right use of "parent" ?

        # Proxy model #####################################

        proxy_model = QSortFilterProxyModel(parent=self)  # TODO: right use of "parent" ?
        proxy_model.setSourceModel(adverts_model)

        self.table_view.setModel(proxy_model)
        #self.table_view.setModel(adverts_model)

        # Set the view ####################################

        #self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)   # Select the full row when a cell is selected (See http://doc.qt.io/qt-5/qabstractitemview.html#selectionBehavior-prop )
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)   # Set selection mode. See http://doc.qt.io/qt-5/qabstractitemview.html#selectionMode-prop

        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)

        self.table_view.horizontalHeader().setStretchLastSection(True)  # http://doc.qt.io/qt-5/qheaderview.html#stretchLastSection-prop

        delegate = AdvertsTableDelegate(data)
        self.table_view.setItemDelegate(delegate)

        # Set key shortcut ################################

        # see https://stackoverflow.com/a/17631703  and  http://doc.qt.io/qt-5/qaction.html#details

        # Add row action

        add_row_action = QAction(self.table_view)
        add_row_action.setShortcut(Qt.CTRL | Qt.Key_N)

        add_row_action.triggered.connect(self.add_row_btn_callback)
        self.table_view.addAction(add_row_action)

        # Delete row action

        del_row_action = QAction(self.table_view)
        del_row_action.setShortcut(Qt.CTRL | Qt.Key_Delete)

        del_row_action.triggered.connect(self.remove_row_callback)
        self.table_view.addAction(del_row_action)

        # Delete cell action

        del_cell_action = QAction(self.table_view)
        del_cell_action.setShortcut(Qt.Key_Delete)

        del_cell_action.triggered.connect(self.remove_cell_callback)
        self.table_view.addAction(del_cell_action)

        # Set slots #######################################

        self.btn_add_row.clicked.connect(self.add_row_btn_callback)


    def add_row_btn_callback(self):
        parent = QModelIndex()                                   # More useful with e.g. tree structures

        row_index = 0                                           # Insert new rows to the begining
        #row_index = self.table_view.model().rowCount(parent)     # Insert new rows to the end

        self.table_view.model().insertRows(row_index, 1, parent)

        #index = self.table_view.model().index(row_index, 0)    # TODO
        #self.table_view.selectionModel().select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)    # TODO

    def remove_row_callback(self):
        parent = QModelIndex()                                   # More useful with e.g. tree structures

        # See http://doc.qt.io/qt-5/model-view-programming.html#handling-selections-in-item-views
        #current_index = self.table_view.selectionModel().currentIndex()
        #print("Current index:", current_index.row(), current_index.column())

        selection_index_list = self.table_view.selectionModel().selectedRows()
        selected_row_list = [selection_index.row() for selection_index in selection_index_list]

        #row_index = 0                                           # Remove the first row
        #row_index = self.table_view.model().rowCount(parent) - 1 # Remove the last row

        # WARNING: the list of rows to remove MUST be sorted in reverse order
        # otherwise the index of rows to remove may change at each iteration of the for loop!

        # TODO: there should be a lock mechanism to avoid model modifications from external sources while iterating this loop...
        #       Or as a much simpler alternative, modify the ItemSelectionMode to forbid the non contiguous selection of rows and remove the following for loop
        for row_index in sorted(selected_row_list, reverse=True):
            # Remove rows one by one to allow the removql of non-contiguously selected rows (e.g. "rows 0, 2 and 3")
            success = self.table_view.model().removeRows(row_index, 1, parent)
            if not success:
                raise Exception("Unknown error...")   # TODO

    def remove_cell_callback(self):
        parent = QModelIndex()                                   # More useful with e.g. tree structures

        # See http://doc.qt.io/qt-5/model-view-programming.html#handling-selections-in-item-views
        current_index = self.table_view.selectionModel().currentIndex()

        self.table_view.model().setData(current_index, None, Qt.EditRole)     # TODO: is it correct to do like this ???

        # TODO: set the row to self.table_view.model().data.default_init_values[current_index.column()] instead ?