"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import Optional
from subprocess import Popen
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget
from toktokkie.metadata.Book import Book
from toktokkie.metadata.components.enums import IdType
from toktokkie.gui.pyuic.book_widget import Ui_BookWidget


class BookWidget(QWidget, Ui_BookWidget):
    """
    Class that defines the behaviour of a Book widget
    """

    def __init__(self, parent: QMainWindow):
        """
        Initializes the widget
        :param parent: The parent window
        """
        super().__init__(parent)
        self.setupUi(self)
        self.metadata = None  # type: Optional[Book]
        self.initialize_buttons()

    def initialize_buttons(self):
        """
        Initializes the widget buttons
        :return: None
        """
        self.open_directory_button.clicked.connect(self.open_directory)
        pass

    def set_metadata(self, metadata: Book):
        """
        Displays the information about a metadata
        :param metadata: The metadata to display
        :return: None
        """
        self.metadata = metadata
        self.name.setText(metadata.name)
        self.tags_edit.setText(", ".join(metadata.tags))
        self.set_icon_image()

    def open_directory(self):
        """
        Opens the directory of the metadata
        :return: None
        """
        Popen(["xdg-open", self.metadata.directory_path]).wait()

    def set_icon_image(self):
        """
        Sets the icon image of a Book Widget
        :return: None
        """
        icon = self.metadata.get_icon_file("main")
        icon_pixmap = QPixmap(icon)
        self.icon_label.setPixmap(icon_pixmap)

    def write_changes(self):
        """
        Writes the changes to the metadata to disk
        :return: None
        """
        self.metadata.tags = self.tags_edit.text().strip().split(",")
        ids = self.metadata.ids
        ids[IdType.ISBN] = self.isbn_edit.text().strip()
        self.metadata.ids = ids
        self.metadata.write()
        self.set_metadata(self.metadata)
