#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QTabWidget

from timemg.qt.widgets.tabs.adverts import AdvertsTab
from timemg.qt.widgets.tabs.stats import StatsTab


class MainWindow(QMainWindow):

    def __init__(self, timemg_data):
        super().__init__()

        self.resize(1200, 900)
        self.setWindowTitle('Time Manager')
        self.statusBar().showMessage("Ready", 2000)

        # Make widgets ####################################

        self.tabs = QTabWidget(parent=self)
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.adverts_tab = AdvertsTab(timemg_data, parent=self.tabs)
        self.stats_tab = StatsTab(timemg_data, parent=self.tabs)

        self.tabs.addTab(self.adverts_tab, "Edit")
        self.tabs.addTab(self.stats_tab, "Stats")

        # Show ############################################

        self.show()
