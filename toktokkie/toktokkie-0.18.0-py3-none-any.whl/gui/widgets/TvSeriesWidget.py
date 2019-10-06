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

import tvdb_api
import webbrowser
from typing import Optional
from subprocess import Popen
from threading import Thread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.components.enums import IdType
from toktokkie.gui.pyuic.tv_show_widget import Ui_TvSeriesWidget


class TvSeriesWidget(QWidget, Ui_TvSeriesWidget):
    """
    Class that defines the behaviour of a TV Series widget
    """

    def __init__(self, parent: QMainWindow):
        """
        Initializes the widget
        :param parent: The parent window
        """
        super().__init__(parent)
        self.setupUi(self)
        self.metadata = None  # type: Optional[TvSeries]
        self.initialize_buttons()

    def initialize_buttons(self):
        """
        Initializes the widget buttons
        :return: None
        """
        self.open_directory_button.clicked.connect(self.open_directory)
        self.tvdb_url_button.clicked.connect(self.open_tvdb_url)
        self.confirm_changes_button.clicked.connect(self.write_changes)

    def set_metadata(self, metadata: TvSeries):
        """
        Displays the information about a metadata
        :param metadata: The metadata to display
        :return: None
        """
        self.metadata = metadata
        self.name.setText(metadata.name)
        self.tags_edit.setText(", ".join(metadata.tags))
        self.tvdb_id_edit.setText(str(metadata.tvdb_id))
        self.set_icon_image()
        Thread(target=self.load_tvdb_info).start()

    def open_directory(self):
        """
        Opens the directory of the metadata
        :return: None
        """
        Popen(["xdg-open", self.metadata.directory_path]).wait()

    def set_icon_image(self):
        """
        Sets the icon image of a TV Series Widget
        :return: None
        """
        icon = self.metadata.get_icon_file("main")
        icon_pixmap = QPixmap(icon)
        self.icon_label.setPixmap(icon_pixmap)

    def open_tvdb_url(self):
        """
        Opens the tvdb URL in a web browser
        :return: None
        """
        tvdb_id = self.tvdb_id_edit.text()
        tvdb_url = "http://www.thetvdb.com/dereferrer/series/{}"\
            .format(tvdb_id)
        webbrowser.open(tvdb_url, new=2)

    def load_tvdb_info(self):
        """
        Loads TVDB data.
        :return: None
        """
        tvdb_data = tvdb_api.Tvdb()[int(self.metadata.tvdb_id)]
        seasons = len(tvdb_data)
        episodes = 0
        for season_number in tvdb_data:
            episodes += len(tvdb_data[season_number])

        self.first_aired_label.setText(tvdb_data.data["firstAired"])
        self.episode_length_label.setText(tvdb_data.data["runtime"])
        self.genres_label.setText(", ".join(tvdb_data.data["genre"]))
        self.amount_of_episodes_label.setText(str(episodes))
        self.amount_of_seasons_label.setText(str(seasons))

    def write_changes(self):
        """
        Writes the changes to the metadata to disk
        :return: None
        """
        self.metadata.tags = self.tags_edit.text().strip().split(",")
        ids = self.metadata.ids
        ids[IdType.TVDB] = self.tvdb_id_edit.text().strip()
        self.metadata.ids = ids
        self.metadata.write()
        self.set_metadata(self.metadata)
