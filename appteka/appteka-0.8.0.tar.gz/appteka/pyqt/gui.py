# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" Helper functions for building Qt GUI. """

from PyQt5 import QtWidgets, QtGui


def add_action(window, name, slot, pic=None, shortcut=None, menu=None):
    """Add action conected with clot to the main window."""
    action = None
    if pic:
        action = QtWidgets.QAction(QtGui.QIcon(pic), name, window)
    else:
        action = QtWidgets.QAction(name, window)
    action.triggered.connect(slot)
    if shortcut:
        action.setShortcut(shortcut)
    if menu is not None:
        menu.addAction(action)
    return action


def add_sublayout(parent_layout, direction="h"):
    """Add sublayout."""
    if direction.lower() == "h":
        layout = QtWidgets.QHBoxLayout()
    elif direction.lower() == "v":
        layout = QtWidgets.QVBoxLayout()
    else:
        return None
    parent_layout.addLayout(layout)
    return layout


def add_button(text, slot, layout):
    """Add button connected with slot to layout."""
    button = QtWidgets.QPushButton(text)
    button.clicked.connect(slot)
    layout.addWidget(button)
    return button


def add_edit(layout):
    """Add line edit to layout."""
    edit = QtWidgets.QLineEdit()
    layout.addWidget(edit)
    return edit


def add_label(text, layout):
    """Add text label to layout."""
    label = QtWidgets.QLabel(text)
    layout.addWidget(label)
    return label


def add_widget(widget, layout):
    """Add widget to layout."""
    layout.addWidget(widget)
    return widget


def show_about(title="About program", name="", version="",
               descr="", parent=None):
    """Show about window."""
    mbox = QtWidgets.QMessageBox(parent)
    mbox.setWindowTitle(title)
    text = "<p><b>{} {}</b></p>".format(name, version)
    text += "<p> {} </p>".format(descr)
    mbox.setText(text)
    mbox.exec()
