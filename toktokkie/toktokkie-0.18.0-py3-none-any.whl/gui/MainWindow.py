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
import json
import time
from threading import Thread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTreeWidgetItem, QWidget
from toktokkie.Directory import Directory
from toktokkie.exceptions import MissingMetadata, InvalidMetadata
from toktokkie.metadata.components.enums import MediaType
from toktokkie.gui.pyuic.main import Ui_MainWindow
from toktokkie.gui.widgets.BookWidget import BookWidget
from toktokkie.gui.widgets.MovieWidget import MovieWidget
from toktokkie.gui.widgets.TvSeriesWidget import TvSeriesWidget
from toktokkie.gui.widgets.TvSeasonWidget import TvSeasonWidget


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The Main Window of the application
    """

    def __init__(self):
        """
        Initializes the main window
        """
        start = time.time()
        super().__init__(None)
        self.setupUi(self)

        self.config_dir = os.path.join(
            os.path.expanduser("~"), ".config/toktokkie"
        )
        self.config_file = os.path.join(self.config_dir, "config.json")
        with open(self.config_file, "r") as f:
            self.config = json.load(f)

        self._initialize_actions()

        self.media = {}
        self.reload()

        self.media_widgets = {
            MediaType.TV_SERIES: TvSeriesWidget(self),
            MediaType.MOVIE: MovieWidget(self),
            MediaType.BOOK: BookWidget(self),
            MediaType.BOOK_SERIES: BookWidget(self),
            "tv_season": TvSeasonWidget(self),
            "default": QWidget(self)
        }
        for _, widget in self.media_widgets.items():
            self.widget_stack.addWidget(widget)
        end = time.time()
        print("Startup Time: {}".format(end-start))

    def reload(self):
        """
        Refreshes the data shown
        :return: None
        """
        self._reload_directories()
        self._display_directories_in_tree()

    def write_config(self):
        """
        Writes the config file to disk
        :return:
        """
        with open(self.config_file, "w") as f:
            json.dump(
                self.config,
                f,
                sort_keys=True,
                indent=4,
                separators=(",", ": ")
            )

    def _initialize_actions(self):
        """
        Initilizes any actions that can be taken
        :return: None
        """
        self.media_tree.currentItemChanged.connect(self._display_media)
        self.add_directories_option.triggered.connect(self._open_add_dialog)
        self.remove_directories_option.triggered.connect(
            self._open_remove_dialog
        )

    def _open_add_dialog(self):
        """
        Opens a dialog window that allows the user to add a new directory
        :return: None
        """
        directory = QFileDialog.getExistingDirectory(self, "Browse")
        if directory:
            self.config["media_directories"].append(directory)
            self.write_config()
            self._reload_directories()
            self._display_directories_in_tree()

    def _open_remove_dialog(self):
        """
        Opens a dialog window that allows the user to remove a previously added
        directory
        :return: None
        """
        pass
        # RemoveDirectoryDialog(self).show()

    def _reload_directories(self):
        """
        Reloads the metadata from the directories specified in the config file
        :return: None
        """
        start = time.time()
        self.media = {}
        for media_type in MediaType:
            self.media[media_type] = []

        for media_directory in self.config["media_directories"]:

            if not os.path.isdir(media_directory):
                continue

            for subdir in os.listdir(media_directory):
                try:
                    media = Directory(os.path.join(media_directory, subdir))
                except (MissingMetadata, InvalidMetadata):
                    continue

                self.media[media.metadata.media_type()].append(media)

        for media_type in self.media:
            self.media[media_type].sort(key=lambda x: x.metadata.name)
        end = time.time()
        print("Loaded directories in {}".format(end - start))

    def _display_directories_in_tree(self):
        """
        Displays the media items' names in the tree
        :return: None
        """
        self.media_tree.clear()
        for media_type, media_directories in self.media.items():
            widget = QTreeWidgetItem([media_type.value])
            for media_directory in media_directories:

                metadata = media_directory.metadata

                icon = metadata.get_icon_file("main")
                subwidget = QTreeWidgetItem([metadata.name])

                if icon is not None:
                    Thread(target=lambda: subwidget.setIcon(0, QIcon(icon)))\
                        .start()

                if metadata.media_type() == MediaType.TV_SERIES:
                    for season in metadata.seasons:

                        season_widget = QTreeWidgetItem([season.name])
                        subwidget.addChild(season_widget)

                widget.addChild(subwidget)

            self.media_tree.addTopLevelItem(widget)

    def _display_media(self, tree_item: QTreeWidgetItem):
        """
        Displays a media item
        :param tree_item: The tree item that got selected
        :return: None
        """

        if tree_item is None or tree_item.parent() is None:
            self.widget_stack.setCurrentWidget(self.media_widgets["default"])
            return

        depth = 0
        depth_check = tree_item
        while depth_check.parent() is not None:
            depth += 1
            depth_check = depth_check.parent()

        if depth == 1:
            series_widget = tree_item
        elif depth == 2:
            series_widget = tree_item.parent()
        else:
            return

        media_type = MediaType(series_widget.parent().data(0, 0))
        index = series_widget.parent().indexOfChild(series_widget)
        metadata = self.media[media_type][index].metadata

        if depth == 1:
            widget = self.media_widgets[media_type]
            widget.set_metadata(metadata)
            self.widget_stack.setCurrentWidget(widget)

        elif depth == 2:

            if metadata.media_type() == MediaType.TV_SERIES:
                season = tree_item.data(0, 0)
                widget = self.media_widgets["tv_season"]
                widget.set_metadata(metadata, season)
                self.widget_stack.setCurrentWidget(widget)
