#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QDateEdit, QTimeEdit, QSpinBox, QComboBox

QT_DATE_FORMAT = "yyyy-MM-dd"   # MUST BE CONSISTENT WITH QT_DATE_TIME_FORMAT
PY_DATE_FORMAT = "%Y-%m-%d"     # MUST BE CONSISTENT WITH PY_DATE_TIME_FORMAT

QT_TIME_FORMAT = "HH:mm"   # MUST BE CONSISTENT WITH QT_TIME_FORMAT
PY_TIME_FORMAT = "%H:%M"     # MUST BE CONSISTENT WITH PY_TIME_FORMAT

class AdvertsTableDelegate(QStyledItemDelegate):

    def __init__(self, data):
        super().__init__()

        self.data = data

        self.date_column_index = data.headers.index("Date")

    def createEditor(self, parent, option, index):
        if index.column() == self.date_column_index:
            editor = QDateEdit(parent=parent)

            #editor.setMinimumDate(datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0))
            #editor.setMaximumDate(datetime.datetime(year=2020, month=9, day=1, hour=18, minute=30))
            editor.setDisplayFormat(QT_DATE_FORMAT)
            #editor.setCalendarPopup(True)

            # setFrame(): tell whether the line edit draws itself with a frame.
            # If enabled (the default) the line edit draws itself inside a frame, otherwise the line edit draws itself without any frame.
            editor.setFrame(False)

            return editor
        else:
            #return QStyledItemDelegate.createEditor(self, parent, option, index)
            editor = QTimeEdit(parent=parent)

            #editor.setMinimumDate(datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0))
            #editor.setMaximumDate(datetime.datetime(year=2020, month=9, day=1, hour=18, minute=30))
            editor.setDisplayFormat(QT_TIME_FORMAT)
            #editor.setCalendarPopup(True)

            # setFrame(): tell whether the line edit draws itself with a frame.
            # If enabled (the default) the line edit draws itself inside a frame, otherwise the line edit draws itself without any frame.
            editor.setFrame(False)

            return editor

    def setEditorData(self, editor, index):

        value = index.model().data(index, Qt.EditRole)

        if value is None:
            value = self.data.default_edit_values[index.column()]

        if isinstance(value, datetime.time):
            editor.setTime(value)     # value cannot be a string, it have to be a datetime...
        elif isinstance(value, datetime.date):
            editor.setDate(value)     # value cannot be a string, it have to be a datetime...
        else:
            raise NotImplementedError()  # TODO

        # if index.column() == self.date_column_index:
        #     value = index.model().data(index, Qt.EditRole)

        #     if value is None:
        #         value = datetime.datetime.now().date()

        #     editor.setDate(value)     # value cannot be a string, it have to be a datetime...
        # else:
        #     value = index.model().data(index, Qt.EditRole)

        #     if value is None:
        #         value = datetime.datetime.now().time()

        #     editor.setTime(value)     # value cannot be a string, it have to be a datetime...

    def setModelData(self, editor, model, index):
        if index.column() == self.date_column_index:
            editor.interpretText()
            str_value = editor.text()
            dt_value = datetime.datetime.strptime(str_value, PY_DATE_FORMAT).date()
            model.setData(index, dt_value, Qt.EditRole)
        else:
            #return QStyledItemDelegate.setModelData(self, editor, model, index)
            editor.interpretText()
            str_value = editor.text()
            dt_value = datetime.datetime.strptime(str_value, PY_TIME_FORMAT).time()
            model.setData(index, dt_value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        if index.column() in (self.date_column_index, ):
            editor.setGeometry(option.rect)
        else:
            return QStyledItemDelegate.updateEditorGeometry(self, editor, option, index)
