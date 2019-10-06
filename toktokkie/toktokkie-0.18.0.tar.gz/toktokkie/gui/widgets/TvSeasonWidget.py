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

import os
import tvdb_api
import requests
import webbrowser
from typing import Optional
from subprocess import Popen
from threading import Thread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QListWidgetItem
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.components.TvSeason import TvSeason
from toktokkie.metadata.components.enums import IdType
from toktokkie.gui.pyuic.tv_season_widget import Ui_TvSeasonWidget


class TvSeasonWidget(QWidget, Ui_TvSeasonWidget):
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
        self.season = None  # type: Optional[TvSeason]
        self.initialize_buttons()

    def initialize_buttons(self):
        """
        Initializes the widget buttons
        :return: None
        """
        self.open_directory_button.clicked.connect(self.open_directory)
        self.tvdb_url_button.clicked.connect(self.open_tvdb_url)
        self.confirm_changes_button.clicked.connect(self.write_changes)

    def set_metadata(self, metadata: TvSeries, season: str):
        """
        Displays the information about a metadata
        :param metadata: The metadata of the series to display
        :param season: The name of the season to display
        :return: None
        """
        self.metadata = metadata
        self.season = metadata.get_season(season)

        self.name.setText(self.metadata.name)
        self.season_name.setText(self.season.name)
        self.tvdb_id_edit.setText(str(self.season.tvdb_id))
        self.set_icon_image()
        self.load_episode_files()
        Thread(target=self.load_tvdb_info).start()

    def open_directory(self):
        """
        Opens the directory of the season metadata
        :return: None
        """
        Popen(["xdg-open", self.season.path]).wait()

    def set_icon_image(self):
        """
        Sets the icon image of a TV Season Widget
        :return: None
        """
        icon = self.metadata.get_icon_file(self.season.name)
        icon_pixmap = QPixmap(icon)
        self.icon_label.setPixmap(icon_pixmap)

    def open_tvdb_url(self):
        """
        Opens the tvdb URL in a web browser
        :return: None
        """
        series_id = self.tvdb_id_edit.text()
        deref_url = "http://www.thetvdb.com/dereferrer/series/{}"\
            .format(series_id)
        series_url = requests.get(deref_url).url

        season_url = "{}/seasons/{}"\
            .format(series_url, self.season.season_number)

        webbrowser.open(season_url, new=2)

    def load_tvdb_info(self):
        """
        Loads TVDB data.
        :return: None
        """
        tvdb_data = tvdb_api.Tvdb()[int(self.season.tvdb_id)]
        if self.season.is_spinoff():
            season_number = 1
        else:
            season_number = self.season.season_number
        season_data = tvdb_data[season_number]
        episode_amount = len(season_data)
        self.amount_of_episodes_label.setText(str(episode_amount))

    def load_episode_files(self):
        """
        Displays the episode files
        :return: None
        """
        self.episode_list.clear()
        for episode_file in sorted(os.listdir(self.season.path)):
            episode_item = QListWidgetItem(episode_file)
            self.episode_list.addItem(episode_item)

    def write_changes(self):
        """
        Writes the changes to the metadata to disk
        :return: None
        """
        ids = self.season.ids
        ids[IdType.TVDB] = self.tvdb_id_edit.text()
        self.season.ids = ids

        seasons = list(filter(
            lambda x: x.name != self.season.name,
            self.metadata.seasons
        ))
        seasons.append(self.season)
        self.metadata.seasons = seasons
        self.metadata.write()
